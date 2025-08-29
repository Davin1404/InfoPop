// API service for FileUpload component
const API_BASE_URL = 'http://localhost:8001'

export interface UploadResponse {
  message: string
  file_id: number
  filename: string
  size: number
}

export interface DocumentInfo {
  id: number
  filename: string
  upload_timestamp: string
}

export class FileUploadService {
  
  static async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/upload-documents`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
    }
    
    return await response.json()
  }
  
  static async getDocuments(): Promise<DocumentInfo[]> {
    const response = await fetch(`${API_BASE_URL}/documents`)
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
    }
    
    return await response.json()
  }
  
  static async deleteDocument(fileId: number): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/documents/${fileId}`, {
      method: 'DELETE'
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
    }
    
    return await response.json()
  }

  static async scanDirectory(directoryPath: string): Promise<{ files: string[], totalSize: number }> {
    // This would need to be implemented with Tauri file system APIs
    // For now, return mock data
    return {
      files: [`${directoryPath}/example1.txt`, `${directoryPath}/example2.pdf`],
      totalSize: 1024000
    }
  }

  // Alias methods for the new FileUpload component
  static async deleteFile(fileId: number): Promise<{ message: string }> {
    return await this.deleteDocument(fileId)
  }

  static async getUploadedFiles(): Promise<Array<{ id: number, name: string, size: number, uploadTime: Date }>> {
    const documents = await this.getDocuments()
    return documents.map(doc => ({
      id: doc.id,
      name: doc.filename,
      size: 0, // Size not available from the current API
      uploadTime: new Date(doc.upload_timestamp)
    }))
  }
}
