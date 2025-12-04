import { create } from 'zustand';
import { filesApi, FileItem, FileListResponse } from '../api/files';

interface FileState {
  items: FileItem[];
  currentPath: string;
  parent: string | null;
  totalSize: number;
  selectedItems: Set<string>;
  sortBy: 'name' | 'size' | 'date';
  sortOrder: 'asc' | 'desc';
  filter: 'all' | 'images' | 'videos' | 'audio' | 'documents';
  viewMode: 'grid' | 'list';
  isLoading: boolean;
  error: string | null;

  fetchFiles: (path?: string) => Promise<void>;
  uploadFiles: (files: File[], path?: string) => Promise<void>;
  deleteSelected: () => Promise<void>;
  moveSelected: (destination: string) => Promise<void>;
  copySelected: (destination: string) => Promise<void>;
  renameFile: (path: string, newName: string) => Promise<void>;
  downloadFile: (path: string) => Promise<void>;
  searchFiles: (query: string) => Promise<void>;

  toggleSelect: (path: string) => void;
  selectAll: () => void;
  clearSelection: () => void;
  setSort: (by: 'name' | 'size' | 'date', order: 'asc' | 'desc') => void;
  setFilter: (filter: string) => void;
  setViewMode: (mode: 'grid' | 'list') => void;
  navigateToPath: (path: string) => void;
  navigateUp: () => void;
}

export const useFileStore = create<FileState>((set, get) => ({
  items: [],
  currentPath: '/',
  parent: null,
  totalSize: 0,
  selectedItems: new Set(),
  sortBy: 'name',
  sortOrder: 'asc',
  filter: 'all',
  viewMode: 'grid',
  isLoading: false,
  error: null,

  fetchFiles: async (path?: string) => {
    const targetPath = path || get().currentPath;
    set({ isLoading: true, error: null });

    try {
      const response = await filesApi.list(
        targetPath,
        get().sortBy,
        get().sortOrder,
        get().filter
      );

      set({
        items: response.items,
        currentPath: response.path,
        parent: response.parent,
        totalSize: response.total_size,
        isLoading: false,
        selectedItems: new Set(),
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch files',
        isLoading: false,
      });
    }
  },

  uploadFiles: async (files: File[], path?: string) => {
    const targetPath = path || get().currentPath;
    set({ isLoading: true });

    try {
      await filesApi.upload(files, targetPath);
      await get().fetchFiles(targetPath);
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Upload failed',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteSelected: async () => {
    const paths = Array.from(get().selectedItems);
    if (paths.length === 0) return;

    set({ isLoading: true });

    try {
      await filesApi.delete(paths);
      await get().fetchFiles();
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Delete failed',
        isLoading: false,
      });
      throw error;
    }
  },

  moveSelected: async (destination: string) => {
    const paths = Array.from(get().selectedItems);
    if (paths.length === 0) return;

    set({ isLoading: true });

    try {
      await filesApi.move(paths, destination);
      await get().fetchFiles();
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Move failed',
        isLoading: false,
      });
      throw error;
    }
  },

  copySelected: async (destination: string) => {
    const paths = Array.from(get().selectedItems);
    if (paths.length === 0) return;

    set({ isLoading: true });

    try {
      await filesApi.copy(paths, destination);
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Copy failed',
        isLoading: false,
      });
      throw error;
    }
  },

  renameFile: async (path: string, newName: string) => {
    set({ isLoading: true });

    try {
      await filesApi.rename(path, newName);
      await get().fetchFiles();
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Rename failed',
        isLoading: false,
      });
      throw error;
    }
  },

  downloadFile: async (path: string) => {
    try {
      const blob = await filesApi.download(path);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = path.split('/').pop() || 'download';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Download failed',
      });
      throw error;
    }
  },

  searchFiles: async (query: string) => {
    set({ isLoading: true, error: null });

    try {
      const response = await filesApi.search(query, get().currentPath);
      set({
        items: response.results || [],
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Search failed',
        isLoading: false,
      });
    }
  },

  toggleSelect: (path: string) => {
    const selected = new Set(get().selectedItems);
    if (selected.has(path)) {
      selected.delete(path);
    } else {
      selected.add(path);
    }
    set({ selectedItems: selected });
  },

  selectAll: () => {
    const allPaths = new Set(get().items.map((item) => item.path));
    set({ selectedItems: allPaths });
  },

  clearSelection: () => {
    set({ selectedItems: new Set() });
  },

  setSort: (by: 'name' | 'size' | 'date', order: 'asc' | 'desc') => {
    set({ sortBy: by, sortOrder: order });
    get().fetchFiles();
  },

  setFilter: (filter: string) => {
    set({ filter: filter as any });
    get().fetchFiles();
  },

  setViewMode: (mode: 'grid' | 'list') => {
    set({ viewMode: mode });
    localStorage.setItem('viewMode', mode);
  },

  navigateToPath: (path: string) => {
    set({ currentPath: path });
    get().fetchFiles(path);
  },

  navigateUp: () => {
    const parent = get().parent;
    if (parent) {
      get().navigateToPath(parent);
    }
  },
}));
