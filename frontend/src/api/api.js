import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 45000,
});

apiClient.interceptors.request.use(
    (config) => {
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

apiClient.interceptors.response.use(
    (response) => response.data,
    (error) => {
        const customError = {
            message: error.response?.data?.detail || error.message || 'An unexpected API error occurred.',
            status: error.response?.status,
            data: error.response?.data,
        };
        return Promise.reject(customError);
    }
);


export const chatApi = {
    /**
     * Create a new chat session
     * @param {Object} payload - { title, complaint_id }
     */
    createChat: async (payload = {}) => {
        return await apiClient.post('/chats/', payload);
    },

    /**
     * Get chat session detail with full message history
     * @param {number} chatId
     */
    getChat: async (chatId) => {
        return await apiClient.get(`/chats/${chatId}`);
    },


    listChats: async (skip = 0, limit = 50) => {
        return await apiClient.get('/chats/', { params: { skip, limit } });
    },

    /**
     * Send user message to AI Copilot
     * @param {number} chatId
     * @param {string} content
     * @param {string} sender
     */
    sendMessage: async (chatId, content, sender = 'user') => {
        return await apiClient.post(`/chats/${chatId}/messages`, {
            content,
            sender,
        });
    },

    /**
     * Delete a chat session
     * @param {number} chatId
     */
    deleteChat: async (chatId) => {
        return await apiClient.delete(`/chats/${chatId}`);
    },
};


export const fileApi = {
    /**
     * Upload an attachment file
     * @param {File} file
     * @param {number|null} chatId
     * @param {number|null} complaintId
     */
    uploadFile: async (file, chatId = null, complaintId = null) => {
        const formData = new FormData();
        formData.append('file', file);
        if (chatId) formData.append('chat_id', chatId);
        if (complaintId) formData.append('complaint_id', complaintId);

        return await apiClient.post('/files/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },


    listFiles: async (chatId = null, complaintId = null) => {
        return await apiClient.get('/files/', {
            params: { chat_id: chatId, complaint_id: complaintId },
        });
    },


    getFile: async (fileId) => {
        return await apiClient.get(`/files/${fileId}`);
    },


    deleteFile: async (fileId) => {
        return await apiClient.delete(`/files/${fileId}`);
    },
};


export const complaintApi = {
    /**
     * Save a new customer complaint record
     * @param {Object} complaintData
     */
    saveComplaint: async (complaintData) => {
        return await apiClient.post('/complaints/', complaintData);
    },


    listComplaints: async (skip = 0, limit = 50) => {
        return await apiClient.get('/complaints/', { params: { skip, limit } });
    },


    getComplaint: async (complaintId) => {
        return await apiClient.get(`/complaints/${complaintId}`);
    },


    checkCompleteness: async (formData, generateEmail = true) => {
        return await apiClient.post('/complaints/check-completeness', {
            form_data: formData,
            generate_email: generateEmail,
        });
    },


    getSavedComplaintCompleteness: async (complaintId, generateEmail = true) => {
        return await apiClient.get(`/complaints/${complaintId}/completeness`, {
            params: { generate_email: generateEmail },
        });
    },


    recommendRootCause: async (formData) => {
        return await apiClient.post('/complaints/recommend-root-cause', {
            form_data: formData,
        });
    },


    recommendSavedRootCause: async (complaintId) => {
        return await apiClient.post(`/complaints/${complaintId}/recommend-root-cause`);
    },


    updateComplaintRcaCapa: async (complaintId, payload) => {
        return await apiClient.patch(`/complaints/${complaintId}/rca-capa`, payload);
    },


    checkDuplicates: async (formData, excludeComplaintId = null) => {
        return await apiClient.post('/complaints/check-duplicates', {
            form_data: formData,
            exclude_complaint_id: excludeComplaintId,
        });
    },


    getSavedComplaintDuplicates: async (complaintId) => {
        return await apiClient.get(`/complaints/${complaintId}/duplicates`);
    },


    evaluateCapaRisk: async (formData) => {
        return await apiClient.post('/complaints/evaluate-capa-risk', {
            form_data: formData,
        });
    },


    getSavedComplaintCapaRisk: async (complaintId) => {
        return await apiClient.get(`/complaints/${complaintId}/evaluate-capa-risk`);
    },
};





export default {
    client: apiClient,
    chat: chatApi,
    file: fileApi,
    complaint: complaintApi,
};
