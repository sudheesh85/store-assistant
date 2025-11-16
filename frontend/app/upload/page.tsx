'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, MessageSquare, CheckCircle, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { authService } from '@/lib/auth';

const DATASET_TYPES = [
  { value: 'sales', label: 'Sales Data', icon: '💰' },
  { value: 'inventory', label: 'Inventory Data', icon: '📦' },
  { value: 'staff', label: 'Staff Data', icon: '👥' },
  { value: 'transactions', label: 'Transactions', icon: '💳' },
];

export default function UploadPage() {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);
  const [selectedType, setSelectedType] = useState<string>('sales');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    setIsClient(true);
    // Check authentication and redirect to login if not authenticated
    if (!authService.isAuthenticated()) {
      router.replace('/login');
    }
  }, [router]);

  // Show loading during SSR and initial client render
  if (!isClient || !authService.isAuthenticated()) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  const detectDatasetType = (filename: string): string => {
    const nameLower = filename.toLowerCase();
    
    // Check for keywords in filename
    if (nameLower.includes('sale') || nameLower.includes('sales')) {
      return 'sales';
    } else if (nameLower.includes('inventory') || nameLower.includes('stock')) {
      return 'inventory';
    } else if (nameLower.includes('staff') || nameLower.includes('employee')) {
      return 'staff';
    } else if (nameLower.includes('transaction')) {
      return 'transactions';
    }
    
    // Default to sales if no match
    return 'sales';
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.name.toLowerCase().endsWith('.csv')) {
      setFile(selectedFile);
      // Automatically detect and set the dataset type from filename
      const detectedType = detectDatasetType(selectedFile.name);
      setSelectedType(detectedType);
      setUploadError(null);
    } else {
      setUploadError('Please select a valid CSV file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file || !selectedType) {
      setUploadError('Please select both a file and dataset type');
      return;
    }

    setUploading(true);
    setUploadError(null);

    try {
      await apiClient.uploadDataset(file, selectedType, {
        storeId: 'demo-store',
      });
      
      setUploadSuccess(true);
      setTimeout(() => {
        router.push('/chat');
      }, 1500);
    } catch (error: any) {
      setUploadError(error.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleContinueToChat = () => {
    router.push('/chat');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 flex items-center justify-center px-4">
      <div className="w-full max-w-lg">
        {/* Simple Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-3">
            AI Store Assistant
          </h1>
          <p className="text-white/90 text-lg">
            Upload your data or continue chatting
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8">
          {uploadSuccess ? (
            <div className="text-center py-8">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Upload Successful! 🎉
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Redirecting to chat...
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Upload CSV File
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                  💡 Tip: Name your file with keywords like "sales", "inventory", "staff", or "transaction" 
                  and we'll automatically detect the type!
                </p>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    {file ? (
                      <div>
                        <CheckCircle className="w-10 h-10 text-green-500 mx-auto mb-2" />
                        <p className="font-semibold text-gray-900 dark:text-white">{file.name}</p>
                        <p className="text-sm text-gray-500 mt-1">{(file.size / 1024).toFixed(2)} KB</p>
                        {/* Show detected type */}
                        <div className="mt-3 inline-flex items-center gap-2 bg-blue-50 dark:bg-blue-900/20 px-3 py-1.5 rounded-full">
                          <span className="text-lg">
                            {DATASET_TYPES.find(t => t.value === selectedType)?.icon}
                          </span>
                          <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                            Detected: {DATASET_TYPES.find(t => t.value === selectedType)?.label}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <Upload className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-700 dark:text-gray-300 font-medium">Click to upload CSV</p>
                        <p className="text-sm text-gray-500 mt-1">Up to 10MB</p>
                      </div>
                    )}
                  </label>
                </div>
              </div>

              {/* Error Message */}
              {uploadError && (
                <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <p className="text-sm text-red-700 dark:text-red-300">{uploadError}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="space-y-3 pt-4">
                <button
                  onClick={handleUpload}
                  disabled={!file || uploading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  {uploading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5" />
                      Upload File
                    </>
                  )}
                </button>

                <button
                  onClick={handleContinueToChat}
                  disabled={uploading}
                  className="w-full bg-white hover:bg-gray-50 dark:bg-gray-700 dark:hover:bg-gray-600 border-2 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white font-semibold py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  <MessageSquare className="w-5 h-5" />
                  Continue to Chat
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

