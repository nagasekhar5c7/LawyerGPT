import { useState, useCallback } from "react";
import * as api from "../services/api";

interface UploadState {
  isUploading: boolean;
  fileName: string | null;
  error: string | null;
  success: boolean;
}

export function useFileUpload() {
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    fileName: null,
    error: null,
    success: false,
  });

  const uploadFile = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setUploadState({
        isUploading: false,
        fileName: file.name,
        error: "Only PDF files are accepted",
        success: false,
      });
      return;
    }

    setUploadState({
      isUploading: true,
      fileName: file.name,
      error: null,
      success: false,
    });

    try {
      await api.uploadDocument(file);
      setUploadState({
        isUploading: false,
        fileName: file.name,
        error: null,
        success: true,
      });
    } catch {
      setUploadState({
        isUploading: false,
        fileName: file.name,
        error: "Upload failed. The backend server may not be running yet.",
        success: false,
      });
    }
  }, []);

  const clearUploadState = useCallback(() => {
    setUploadState({
      isUploading: false,
      fileName: null,
      error: null,
      success: false,
    });
  }, []);

  return { uploadState, uploadFile, clearUploadState };
}
