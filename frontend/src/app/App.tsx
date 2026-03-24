import { useState } from "react";
import { Activity, Layers, ArrowLeftRight, Coins, Image } from "lucide-react";
import { Header } from "./components/Header";
import { InputPanel } from "./components/InputPanel";
import { StatusAlert, AlertType } from "./components/StatusAlert";
import { MetricCard } from "./components/MetricCard";
import { DataTable, TableLink, TableBadge } from "./components/DataTable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import {
  mockTransactions,
  mockTransfers,
  mockDeFiActivities,
  mockNFTActivities,
} from "./data/mockData";

interface AnalysisResult {
  address: string;
  classification: "exchange" | "not a exchange";
  transactionCount: number;
  alreadyInDB: boolean;
  data: {
    transactions: any[];
    transfers: any[];
    defi: any[];
    nft: any[];
  };
  alert: {
    type: AlertType;
    message: string;
  } | null;
}

export default function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleAnalyze = async (
    address: string,
    startDate: string,
    endDate: string
  ) => {
    setIsLoading(true);
    setResult(null);

    // Format dates (remove 'T' from datetime-local input)
    const formattedStart = startDate.replace("T", " ");
    const formattedEnd = endDate.replace("T", " ");

    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          address,
          start_date: formattedStart,
          end_date: formattedEnd,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Analysis failed");
      }

      const data = await response.json();

      let alertMessage = "";
      let alertType: AlertType = "success";

      if (data.alreadyInDB) {
        alertMessage = "This address is already available in the main DB";
        alertType = "warning";
      } else if (data.classification === "exchange") {
        alertMessage = "Address classified as exchange. Appended to Address Type DB";
        alertType = "info";
      } else {
        alertMessage = `Address classified as not exchange. Appended ${
          data.data.transactions.length +
          data.data.transfers.length +
          data.data.defi.length +
          data.data.nft.length
        } rows to Active DB.`;
      }

      setResult({
        ...data,
        alert: {
          type: alertType,
          message: alertMessage,
        },
      });
    } catch (error: any) {
      console.error("Analysis error:", error);
      setResult({
        address,
        classification: "not a exchange",
        transactionCount: 0,
        alreadyInDB: false,
        data: { transactions: [], transfers: [], defi: [], nft: [] },
        alert: {
          type: "error",
          message: error.message || "An unexpected error occurred",
        },
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Define table columns
  const transactionColumns = [
    {
      key: "signature",
      label: "Signature",
      render: (value: string) => (
        <TableLink href={`https://solscan.io/tx/${value}`}>
          <code className="text-xs">{value}</code>
        </TableLink>
      ),
    },
    { key: "block", label: "Block" },
    { key: "time", label: "Time" },
    {
      key: "action",
      label: "Action",
      render: (value: string) => <TableBadge variant="outline">{value}</TableBadge>,
    },
    {
      key: "by",
      label: "By",
      render: (value: string) => <code className="text-xs">{value}</code>,
    },
    { key: "value", label: "Value (SOL)", align: "right" as const },
    { key: "fee", label: "Fee", align: "right" as const },
    { key: "programs", label: "Programs" },
  ];

  const transferColumns = [
    {
      key: "from",
      label: "From",
      render: (value: string) => <code className="text-xs">{value}</code>,
    },
    {
      key: "to",
      label: "To",
      render: (value: string) => <code className="text-xs">{value}</code>,
    },
    { key: "amount", label: "Amount", align: "right" as const },
    {
      key: "token",
      label: "Token",
      render: (value: string) => <TableBadge>{value}</TableBadge>,
    },
    {
      key: "action",
      label: "Action",
      render: (value: string) => (
        <TableBadge variant={value === "Send" ? "secondary" : "outline"}>
          {value}
        </TableBadge>
      ),
    },
  ];

  const defiColumns = [
    {
      key: "action",
      label: "Action",
      render: (value: string) => <TableBadge variant="outline">{value}</TableBadge>,
    },
    { key: "platform", label: "Platform" },
    { key: "source", label: "Source" },
    { key: "amount", label: "Amount" },
    { key: "value", label: "Value", align: "right" as const },
  ];

  const nftColumns = [
    { key: "nftName", label: "NFT Name" },
    { key: "price", label: "Price", align: "right" as const },
    { key: "collection", label: "Collection" },
    {
      key: "marketplace",
      label: "Marketplace",
      render: (value: string) => <TableBadge variant="secondary">{value}</TableBadge>,
    },
    {
      key: "fromTo",
      label: "From → To",
      render: (value: string) => <code className="text-xs">{value}</code>,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="container mx-auto px-6 py-8">
        {/* Input Section */}
        <section className="mb-6">
          <InputPanel onAnalyze={handleAnalyze} isLoading={isLoading} />
        </section>

        {/* Results Section */}
        {result && (
          <>
            {/* Alert Section */}
            {result.alert && (
              <section className="mb-6">
                <StatusAlert
                  type={result.alert.type}
                  message={result.alert.message}
                />
              </section>
            )}

            {/* Metrics Section */}
            <section className="mb-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <MetricCard
                  title="Total Transactions"
                  value={result.transactionCount.toLocaleString()}
                  icon={Activity}
                />
                <MetricCard
                  title="Address Classification"
                  value={
                    result.classification === "exchange"
                      ? "Exchange"
                      : "Not Exchange"
                  }
                  icon={Layers}
                  badge={{
                    label:
                      result.classification === "exchange"
                        ? "Exchange"
                        : "Not Exchange",
                    variant:
                      result.classification === "exchange"
                        ? "destructive"
                        : "success",
                  }}
                />
              </div>
            </section>

            {/* Tabs Section */}
            <section>
              <Tabs defaultValue="transactions" className="space-y-6">
                <TabsList className="bg-white border border-gray-200 p-1">
                  <TabsTrigger value="transactions" className="gap-2">
                    <Activity className="h-4 w-4" />
                    Transactions
                  </TabsTrigger>
                  <TabsTrigger value="transfers" className="gap-2">
                    <ArrowLeftRight className="h-4 w-4" />
                    Transfers
                  </TabsTrigger>
                  <TabsTrigger value="defi" className="gap-2">
                    <Coins className="h-4 w-4" />
                    DeFi Activities
                  </TabsTrigger>
                  <TabsTrigger value="nft" className="gap-2">
                    <Image className="h-4 w-4" />
                    NFT Activities
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="transactions">
                  <div className="bg-white rounded-lg p-6 shadow-sm">
                    <DataTable
                      columns={transactionColumns}
                      data={result.data.transactions}
                      isLoading={isLoading}
                      emptyMessage="No transactions found in this range"
                    />
                  </div>
                </TabsContent>

                <TabsContent value="transfers">
                  <div className="bg-white rounded-lg p-6 shadow-sm">
                    <DataTable
                      columns={transferColumns}
                      data={result.data.transfers}
                      isLoading={isLoading}
                      emptyMessage="No transfers found in this range"
                    />
                  </div>
                </TabsContent>

                <TabsContent value="defi">
                  <div className="bg-white rounded-lg p-6 shadow-sm">
                    <DataTable
                      columns={defiColumns}
                      data={result.data.defi}
                      isLoading={isLoading}
                      emptyMessage="No DeFi activities found"
                    />
                  </div>
                </TabsContent>

                <TabsContent value="nft">
                  <div className="bg-white rounded-lg p-6 shadow-sm">
                    <DataTable
                      columns={nftColumns}
                      data={result.data.nft}
                      isLoading={isLoading}
                      emptyMessage="No NFT activities found"
                    />
                  </div>
                </TabsContent>
              </Tabs>
            </section>
          </>
        )}

        {/* Empty State */}
        {!result && !isLoading && (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center p-4 bg-indigo-100 rounded-full mb-4">
              <Activity className="h-8 w-8 text-indigo-600" />
            </div>
            <h3 className="text-gray-900 mb-2">Ready to Analyze</h3>
            <p className="text-gray-500">
              Enter a Solana wallet address and date range to begin analysis
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t bg-white mt-12">
        <div className="container mx-auto px-6 py-4">
          <div className="text-center text-sm text-gray-500">
            <p>Powered by Helius API • Data for analysis purposes only</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
