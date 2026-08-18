import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  initialized: true,
};

export const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setInitialized: (state, action) => {
      state.initialized = action.payload;
    },
  },
});

export const { setInitialized } = appSlice.actions;
export default appSlice.reducer;
