"use client";

import React, { useState } from "react";
import { Upload, Loader2, FileText, CheckCircle2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { cn } from "@/lib/utils";

interface SalesUploadProps {
  onAnalysisComplete: (data: any) => void;
  onAnalysisError: (error: string) => void;
}

export function SalesUpload({ onAnalysisComplete, onAnalysisError }: SalesUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"IDLE" | "UPLOADING" | "ANALYZING">("IDLE");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus("UPLOADING");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/v1/sales-intelligence/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Analysis failed");
      }

      setStatus("ANALYZING");
      const data = await response.json();
      onAnalysisComplete(data);
      setStatus("IDLE");
      setFile(null);
    } catch (error: any) {
      onAnalysisError(error.message);
      setStatus("IDLE");
    }
  };

  return (
    <DashboardCard
      title="Upload Sales Data"
      caption="Upload your transaction history (CSV or Excel) to unlock sales intelligence and demand forecasting."
    >
      <div className="flex flex-col items-center justify-center gap-6 py-8">
        <div
          className={cn(
            "relative flex h-48 w-full max-w-md cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed transition-all",
            file ? "border-primary bg-primary/5" : "border-muted-foreground/20 hover:border-primary/50",
            status !== "IDLE" && "pointer-events-none opacity-60"
          )}
          onClick={() => document.getElementById("file-upload")?.click()}
        >
          <input
            id="file-upload"
            type="file"
            className="hidden"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
          />

          {status === "IDLE" ? (
            <>
              <div className="rounded-full bg-primary/10 p-4 text-primary">
                <Upload className="size-8" />
              </div>
              <p className="mt-4 text-sm font-medium text-foreground">
                {file ? file.name : "Click to upload or drag and drop"}
              </p>
              <p className="text-xs text-muted-foreground">CSV, XLSX (Max 10MB)</p>
            </>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="size-10 animate-spin text-primary" />
              <p className="text-sm font-medium text-foreground">
                {status === "UPLOADING" ? "Uploading file..." : "Analyzing patterns..."}
              </p>
            </div>
          )}
        </div>

        <Button
          onClick={handleUpload}
          disabled={!file || status !== "IDLE"}
          className="min-w-[200px]"
        >
          {status === "IDLE" ? "Analyze Sales Data" : "Processing..."}
        </Button>
      </div>
    </DashboardCard>
  );
}
