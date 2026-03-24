import { Alert, AlertDescription } from "./ui/alert";
import {
  CheckCircle2,
  AlertTriangle,
  Info,
  XCircle,
} from "lucide-react";

export type AlertType = "success" | "warning" | "info" | "error";

interface StatusAlertProps {
  type: AlertType;
  message: string;
}

const alertConfig = {
  success: {
    icon: CheckCircle2,
    className: "border-green-200 bg-green-50 text-green-800",
    iconClassName: "text-green-600",
  },
  warning: {
    icon: AlertTriangle,
    className: "border-yellow-200 bg-yellow-50 text-yellow-800",
    iconClassName: "text-yellow-600",
  },
  info: {
    icon: Info,
    className: "border-blue-200 bg-blue-50 text-blue-800",
    iconClassName: "text-blue-600",
  },
  error: {
    icon: XCircle,
    className: "border-red-200 bg-red-50 text-red-800",
    iconClassName: "text-red-600",
  },
};

export function StatusAlert({ type, message }: StatusAlertProps) {
  const config = alertConfig[type];
  const Icon = config.icon;

  return (
    <Alert className={config.className}>
      <Icon className={`h-4 w-4 ${config.iconClassName}`} />
      <AlertDescription className="ml-2">{message}</AlertDescription>
    </Alert>
  );
}
