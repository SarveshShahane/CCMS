import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  initialized: true,
  activeView: 'form', // 'form' | 'list'
};

export const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setInitialized: (state, action) => {
      state.initialized = action.payload;
    },
    setActiveView: (state, action) => {
      state.activeView = action.payload;
    },
  },
});

export const { setInitialized, setActiveView } = appSlice.actions;
export default appSlice.reducer;
