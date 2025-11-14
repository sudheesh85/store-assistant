'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, FileText, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { authService } from '@/lib/auth';

const DATASET_TYPES = [
  { value: 'sales', label: 'Sales Data', description: 'Transaction records, revenue, products sold', icon: '💰' },
  { value: 'inventory', label: 'Inventory Data', description: 'Stock levels, products, suppliers', icon: '📦' },
  { value: 'staff', label: 'Staff Data', description: 'Employee information, roles, schedules', icon: '👥' },
  { value: 'transactions', label: 'Transactions', description: 'Financial transactions and payments', icon: '💳' },
];

export default function UploadPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedType, setSelectedType] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [skipUpload, setSkipUpload] = useState(false);

  useEffect(() => {
    // Check authentication
    const auth = authService.getAuth();
    
    if (!auth || !auth.isAuthenticated) {
      // Redirect to login if not authenticated
      router.push('/login');
      return;
    }
    
    setIsAuthenticated(true);
    setIsLoading(false);
    
    // Set up API client with auth
    if (auth.token) {
      apiClient.setAuth(auth.token);
    } else if (auth.apiKey) {
      apiClient.setAuth(undefined, auth.apiKey);
    }
  }, [router]);

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  // Don't render if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.name.toLowerCase().endsWith('.csv')) {
      setFile(selectedFile);
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

  const handleSkipToChat = () => {
    setSkipUpload(true);
    setTimeout(() => {
      router.push('/chat');
    }, 500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 flex items-center justify-center px-4">
      <div className="w-full max-w-2xl">
        {/* Simple Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Upload Your Data
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Upload CSV files or continue to chat with existing data
          </p>
        </div>

        {/* Main Upload Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
            
            {uploadSuccess ? (
              <div className="text-center py-12">
                <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Upload Successful! 🎉
                </h2>
                <p className="text-gray-600 dark:text-gray-300">
                  Redirecting to chat...
                </p>
              </div>
            ) : (
              <>
                {/* Dataset Type Selection */}
                <div className="mb-8">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">
                    1. Select Data Type
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {DATASET_TYPES.map((type) => (
                      <button
                        key={type.value}
                        onClick={() => setSelectedType(type.value)}
                        className={`p-4 rounded-xl border-2 transition-all text-left ${
                          selectedType === type.value
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-3xl">{type.icon}</span>
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                              {type.label}
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {type.description}
                            </p>
                          </div>
                          {selectedType === type.value && (
                            <CheckCircle className="w-5 h-5 text-primary-500 flex-shrink-0" />
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* File Upload */}
                <div className="mb-8">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">
                    2. Upload CSV File
                  </label>
                  <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center hover:border-primary-400 dark:hover:border-primary-500 transition-colors">
                    <input
                      type="file"
                      accept=".csv"
                      onChange={handleFileChange}
                      className="hidden"
                      id="file-upload"
                    />
                    <label
                      htmlFor="file-upload"
                      className="cursor-pointer flex flex-col items-center"
                    >
                      {file ? (
                        <>
                          <FileText className="w-12 h-12 text-green-500 mb-3" />
                          <p className="text-lg font-semibold text-gray-900 dark:text-white">
                            {file.name}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {(file.size / 1024).toFixed(2)} KB
                          </p>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.preventDefault();
                              setFile(null);
                            }}
                            className="mt-3 text-sm text-primary-600 dark:text-primary-400 hover:underline"
                          >
                            Choose different file
                          </button>
                        </>
                      ) : (
                        <>
                          <Upload className="w-12 h-12 text-gray-400 mb-3" />
                          <p className="text-lg font-medium text-gray-900 dark:text-white mb-1">
                            Click to upload or drag and drop
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            CSV files only, up to 10MB
                          </p>
                        </>
                      )}
                    </label>
                  </div>
                </div>

                {/* Error Message */}
                {uploadError && (
                  <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-red-900 dark:text-red-200">Upload Failed</p>
                      <p className="text-sm text-red-700 dark:text-red-300">{uploadError}</p>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="space-y-3">
                  <button
                    onClick={handleUpload}
                    disabled={!file || !selectedType || uploading}
                    className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-4 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
                  >
                    {uploading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        Upload CSV
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleSkipToChat}
                    disabled={uploading || skipUpload}
                    className="w-full bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-gray-900 dark:text-white font-semibold py-4 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
                  >
                    {skipUpload ? (
                      'Redirecting...'
                    ) : (
                      <>
                        Continue to Chat
                        <ArrowRight className="w-5 h-5" />
                      </>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

