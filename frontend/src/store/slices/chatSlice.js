import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { chatApi, fileApi } from '../../api/api';
import { autoFillFromAI } from './complaintSlice';

// Async Thunk: Initialize or Create Active Chat Session
export const initChatSessionThunk = createAsyncThunk(
  'chat/initSession',
  async (existingChatId = null, { rejectWithValue }) => {
    try {
      if (existingChatId) {
        const detail = await chatApi.getChat(existingChatId);
        return detail;
      }
      const newChat = await chatApi.createChat({ title: 'AI Copilot Complaint Session' });
      return newChat;
    } catch (err) {
      return rejectWithValue(err.message || 'Failed to initialize chat session');
    }
  }
);

// Async Thunk: Send Message to AI Copilot
export const sendMessageThunk = createAsyncThunk(
  'chat/sendMessage',
  async ({ chatId, content }, { dispatch, rejectWithValue }) => {
    try {
      const response = await chatApi.sendMessage(chatId, content);
      
      // Auto-fill form fields if AI extracted structured data
      if (response.extracted_data) {
        dispatch(autoFillFromAI(response.extracted_data));
      }

      return response;
    } catch (err) {
      return rejectWithValue(err.message || 'Failed to send message to AI Copilot');
    }
  }
);

// Async Thunk: Upload Attachment File
export const uploadChatFileThunk = createAsyncThunk(
  'chat/uploadFile',
  async ({ file, chatId }, { rejectWithValue }) => {
    try {
      const fileRes = await fileApi.uploadFile(file, chatId);
      return fileRes;
    } catch (err) {
      return rejectWithValue(err.message || 'Failed to upload attachment file');
    }
  }
);

export const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    activeChatId: null,
    messages: [],
    uploadedFiles: [],
    isLoading: false,
    isUploading: false,
    error: null,
  },
  reducers: {
    clearChatError: (state) => {
      state.error = null;
    },
    resetChatSession: (state) => {
      state.activeChatId = null;
      state.messages = [];
      state.uploadedFiles = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // initChatSessionThunk
      .addCase(initChatSessionThunk.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(initChatSessionThunk.fulfilled, (state, action) => {
        state.isLoading = false;
        state.activeChatId = action.payload.id;
        state.messages = action.payload.messages || [];
      })
      .addCase(initChatSessionThunk.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'Could not load chat session';
      })

      // sendMessageThunk
      .addCase(sendMessageThunk.pending, (state, action) => {
        state.isLoading = true;
        state.error = null;
        // Optimistically add user message to UI
        state.messages.push({
          id: Date.now(),
          chat_id: action.meta.arg.chatId,
          sender: 'user',
          content: action.meta.arg.content,
          created_at: new Date().toISOString(),
        });
      })
      .addCase(sendMessageThunk.fulfilled, (state, action) => {
        state.isLoading = false;
        // Replace or append AI message
        if (action.payload.ai_message) {
          state.messages.push({
            ...action.payload.ai_message,
            extracted_data: action.payload.extracted_data,
          });
        }
      })
      .addCase(sendMessageThunk.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'Failed to receive AI response';
      })

      // uploadChatFileThunk
      .addCase(uploadChatFileThunk.pending, (state) => {
        state.isUploading = true;
        state.error = null;
      })
      .addCase(uploadChatFileThunk.fulfilled, (state, action) => {
        state.isUploading = false;
        const fileData = action.payload;
        state.uploadedFiles.push(fileData);
        // Append visual upload confirmation message in chat
        state.messages.push({
          id: Date.now(),
          chat_id: state.activeChatId,
          sender: 'system',
          content: `📎 File attachment added: "${fileData.filename}" (${(fileData.file_size / 1024).toFixed(1)} KB)`,
          created_at: new Date().toISOString(),
        });
      })
      .addCase(uploadChatFileThunk.rejected, (state, action) => {
        state.isUploading = false;
        state.error = action.payload || 'Failed to upload file';
      });
  },
});

export const { clearChatError, resetChatSession } = chatSlice.actions;
export default chatSlice.reducer;
