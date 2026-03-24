import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon?: LucideIcon;
  badge?: {
    label: string;
    variant: "default" | "destructive" | "success";
  };
}

export function MetricCard({ title, value, icon: Icon, badge }: MetricCardProps) {
  return (
    <Card className="p-6 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-500">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <p className="font-semibold text-gray-900">{value}</p>
          </div>
          {badge && (
            <Badge
              variant={badge.variant === "success" ? "outline" : badge.variant}
              className={`mt-3 ${
                badge.variant === "success"
                  ? "border-green-200 bg-green-50 text-green-700"
                  : badge.variant === "destructive"
                  ? "bg-red-500 text-white"
                  : ""
              }`}
            >
              {badge.label}
            </Badge>
          )}
        </div>
        {Icon && (
          <div className="p-2 bg-indigo-100 rounded-lg">
            <Icon className="h-5 w-5 text-indigo-600" />
          </div>
        )}
      </div>
    </Card>
  );
}
