from permission.logics import PermissionLogic
from permission.utils.field_lookup import field_lookup

import logging
logger = logging.getLogger(__name__)

class InGroupPermissionLogic(PermissionLogic):
  """ Non-object specific permission that grants permission if the user
      is in a given stek group (Bestuur/Kring/...) regardless of the object passed.
      So ONLY apply this logic to a model if the logic applies to every instance of this model.

      `get_group` should be a getter for said group that returns None on error.
      If the group is None, no permission is granted.
  """

  def __init__(self, grants, get_group):
    self.get_group = get_group
    self.grants = grants

  def has_perm(self, user, perm, obj=None):
    group = self.get_group()

    if not user.is_authenticated() or perm not in self.grants or group is None:
      return False

    # check if lid in group
    # if user is in group this logic grants permission for any passed object
    in_group = group.leden.filter(user__user__pk=user.pk).exists()
    if in_group:
      return True

    return False

class UserAttributePermissionLogic(PermissionLogic):
  """ Non-object specific permission that grants permission if the user
      has an attribute that has one of the required values provided.
      So ONLY apply this logic to a model if the logic applies to every instance of this model.

      example:
        UserAttributePermissionLogic(
          grants=['somemodel.view'],
          attr_name='status',
          required_values=[ Profiel.STATUS.LID ],
        )
  """

  def __init__(self, grants, attr_name, required_values):
    self.attr_name = attr_name
    self.required_values = required_values
    self.grants = grants

  def has_perm(self, user, perm, obj=None):
    if not user.is_authenticated() or perm not in self.grants:
      return False

    value = field_lookup(user, self.attr_name)

    # check if user has required value
    # if user has required value the logic grants permission for any passed object
    if value in self.required_values:
      return True

    return False

class MatchFieldPermissionLogic(PermissionLogic):
  """ Permission logic focussed around granting view-, change- and/or delete permissions.
      Based on a user attribute that should match an object attribute

      example (match verticales to grant view rights on somemodel):
        MatchFieldPermissionLogic(
          grants=['somemodel.view'],
          user_attr='verticale',
          obj_attr='verticale',
        )

      IMPORTANT NOTE: this logic can easily be replaced by a (much more efficient) query that
      filters based on the field match, e.g:
      This is preferable and can e.g. be implemented on the model as:

      def get_viewable_by(self, user):
        return SomeModel.objects.filter(verticale=request.user.profiel.verticale)
  """

  def __init__(self, grants, user_attr, obj_attr):
    self.grants = grants
    self.user_attr = user_attr
    self.obj_attr = obj_attr

  def has_perm(self, user, perm, obj=None):
    if not user.is_authenticated() or perm not in self.grants:
      return False

    if obj is None:
      return True
    elif user.is_active and field_lookup(user, self.user_attr) == field_lookup(obj, self.obj_attr):
      return True

    return False

class DynamicConditionLogic(PermissionLogic):

  def __init__(self, grants, condition_field):
    self.grants = grants
    self.condition_field = condition_field

  def has_perm(self, user, perm, obj):
    if not user.is_authenticated() or perm not in self.grants:
      return False

    if obj is None:
      return True
    else:
      return self.check_dynamic_condition(user, field_lookup(obj, self.condition_field))

    return False

  def check_dynamic_condition(self, user, condition):
    # empty conditions are easy
    if condition == "":
      return True

    try:
      cond, value = condition.split(':', 1)

      if cond == 'lidjaar':
        return user.profiel.lidjaar == int(value)
      elif cond == 'verticale':
        return user.profiel.verticale().naam.upper() == value.upper()

      return False
    except Exception as e:
      return False
