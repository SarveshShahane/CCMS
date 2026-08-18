import { configureStore } from '@reduxjs/toolkit';
import appReducer from './slices/appSlice';
import complaintReducer from './slices/complaintSlice';
import chatReducer from './slices/chatSlice';

export const store = configureStore({
  reducer: {
    app: appReducer,
    complaint: complaintReducer,
    chat: chatReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store;
