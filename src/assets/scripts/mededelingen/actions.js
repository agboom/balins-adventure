import * as types from './constants';

export function addMededeling(vervaltijd, titel, tekst, prioriteit, plaatje) {
  return {
    type: types.ADD_MEDEDELING,
    vervaltijd,
    titel,
    tekst,
    prioriteit,
    plaatje
  };
}

export function deleteMededeling(id) {
  return {
    type: types.DELETE_MEDEDELING,
    id
  };
}

export function editMededeling(id, vervaltijd, titel, tekst, prioriteit, plaatje) {
  return {
    type: types.EDIT_TODO,
    id,
    vervaltijd,
    titel,
    tekst,
    prioriteit,
    plaatje
  };
}
