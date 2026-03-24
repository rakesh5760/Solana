import { Activity, CheckCircle2 } from "lucide-react";
import { Badge } from "./ui/badge";

export function Header() {
  return (
    <header className="border-b bg-white">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">
                Solana Address Classifier
              </h1>
              <p className="text-sm text-gray-500">
                Analyze wallet activity using Helius API
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge
              variant="outline"
              className="gap-1.5 border-green-200 bg-green-50 text-green-700"
            >
              <CheckCircle2 className="h-3.5 w-3.5" />
              API Active
            </Badge>
          </div>
        </div>
      </div>
    </header>
  );
}
