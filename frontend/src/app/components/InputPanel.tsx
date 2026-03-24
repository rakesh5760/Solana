import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { Card } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Button } from "./ui/button";

interface InputPanelProps {
  onAnalyze: (address: string, startDate: string, endDate: string) => void;
  isLoading?: boolean;
}

export function InputPanel({ onAnalyze, isLoading = false }: InputPanelProps) {
  const [address, setAddress] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [isValid, setIsValid] = useState(true);

  const validateAddress = (addr: string) => {
    // Basic validation: Solana addresses are typically 32-44 characters
    const isValidFormat = addr.length >= 32 && addr.length <= 44;
    setIsValid(isValidFormat || addr.length === 0);
    return isValidFormat;
  };

  const handleAddressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setAddress(value);
    validateAddress(value);
  };

  const handleAnalyze = () => {
    if (validateAddress(address) && address && startDate && endDate) {
      onAnalyze(address, startDate, endDate);
    }
  };

  return (
    <Card className="p-6 shadow-sm">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="lg:col-span-2">
          <Label htmlFor="address" className="text-gray-700">
            Wallet Address
          </Label>
          <Input
            id="address"
            type="text"
            placeholder="Enter Solana address"
            value={address}
            onChange={handleAddressChange}
            className={`mt-1.5 ${
              !isValid
                ? "border-red-500 focus-visible:ring-red-500"
                : "border-gray-300"
            }`}
          />
          {!isValid && (
            <p className="mt-1.5 text-sm text-red-600">
              Please enter a valid Solana address
            </p>
          )}
        </div>

        <div>
          <Label htmlFor="start-date" className="text-gray-700">
            Start Date & Time
          </Label>
          <Input
            id="start-date"
            type="datetime-local"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="mt-1.5 border-gray-300"
          />
        </div>

        <div>
          <Label htmlFor="end-date" className="text-gray-700">
            End Date & Time
          </Label>
          <Input
            id="end-date"
            type="datetime-local"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="mt-1.5 border-gray-300"
          />
        </div>

        <div className="lg:col-span-2">
          <Button
            onClick={handleAnalyze}
            disabled={!address || !startDate || !endDate || !isValid || isLoading}
            className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Analyze Address
              </>
            )}
          </Button>
        </div>
      </div>
    </Card>
  );
}
