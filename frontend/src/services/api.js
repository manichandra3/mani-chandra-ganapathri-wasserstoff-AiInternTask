import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Error uploading document');
  }
};

export const searchDocuments = async (query) => {
  try {
    const response = await api.get('/search', {
      params: { query },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Error searching documents');
  }
};

export const askQuestion = async (question) => {
  try {
    const response = await api.get('/ask', {
      params: { question },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Error getting answer');
  }
};

export const deleteDocument = async (documentId) => {
  try {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to delete document');
  }
};

export const getDocumentDetails = async (documentId) => {
  try {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Error fetching document details');
  }
};

export default api; 