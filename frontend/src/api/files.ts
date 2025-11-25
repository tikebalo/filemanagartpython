import apiClient from './client';

export interface FileItem {
  name: string;
  type: 'file' | 'folder';
  path: string;
  size?: number;
  mime?: string;
  modified: string;
  thumbnail?: string;
  is_favorite: boolean;
  items_count?: number;
}

export interface FileListResponse {
  items: FileItem[];
  path: string;
  parent: string | null;
  total_size: number;
}

export const filesApi = {
  list: async (
    path: string = '/',
    sort: string = 'name',
    order: string = 'asc',
    filter?: string
  ): Promise<FileListResponse> => {
    const params: any = { path, sort, order };
    if (filter) params.filter = filter;
    const response = await apiClient.get('/api/files/', { params });
    return response.data;
  },

  upload: async (files: File[], path: string = '/'): Promise<any> => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));

    const response = await apiClient.post(`/api/files/upload?path=${path}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  download: async (path: string): Promise<Blob> => {
    const response = await apiClient.get('/api/files/download', {
      params: { path },
      responseType: 'blob',
    });
    return response.data;
  },

  delete: async (paths: string[]): Promise<any> => {
    const response = await apiClient.delete('/api/files/', {
      params: { paths },
    });
    return response.data;
  },

  rename: async (path: string, newName: string): Promise<any> => {
    const response = await apiClient.put('/api/files/rename', {
      path,
      new_name: newName,
    });
    return response.data;
  },

  move: async (paths: string[], destination: string): Promise<any> => {
    const response = await apiClient.put('/api/files/move', {
      paths,
      destination,
    });
    return response.data;
  },

  copy: async (paths: string[], destination: string): Promise<any> => {
    const response = await apiClient.put('/api/files/copy', {
      paths,
      destination,
    });
    return response.data;
  },

  search: async (query: string, path: string = '/', recursive: boolean = true): Promise<any> => {
    const response = await apiClient.post('/api/files/search', {
      query,
      path,
      recursive,
    });
    return response.data;
  },
};
