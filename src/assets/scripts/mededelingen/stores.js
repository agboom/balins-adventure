import * as types from 'constants';

const initialState = [{
  vervaltijd: new Date(),
  titel: "Hoi",
  tekst: "Mededelinglichaam",
  prioriteit: 0,
  plaatje: "mededeling.jpg",
  id: 0
}];

export default function mededelingen(state = initialState, action) {
  switch (action.type) {
  case types.ADD_MEDEDELING:
    return [{
      id: (state.length === 0) ? 0 : state[0].id + 1,
      vervaltijd: action.vervaltijd,
      titel: action.titel,
      tekst: action.tekst,
      prioriteit: action.prioriteit,
      plaatje: action.plaatje
    }, ...state];

  case types.DELETE_MEDEDELING:
    return state.filter(mededeling =>
      mededeling.id !== action.id
    );

  default:
    return state;
  }
}
