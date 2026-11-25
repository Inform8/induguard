export interface SensorReadings {
  temperature: number;
  vibration: number;
  humidity: number;
  pressure: number;
  energy_consumption: number;
}

export interface ConditionResult {
  timestamp: string;
  machine_id: string;
  status: 'NORMAL' | 'WARNING' | 'CRITICAL' | 'ERROR';
  anomaly: boolean;
  anomaly_score: number;
  predicted_fault: string;
  fault_confidence: number;
  condition: string;
  reasons: string[];
  recommended_action: string;
  risk_level?: string;
  remaining_useful_life?: number;
  sensor_readings?: SensorReadings;
  error?: boolean;
  error_message?: string;
}

export interface Alert {
  id?: string;
  alert_id?: string;
  machine_id: string;
  timestamp: string;
  status?: string;
  severity?: string;
  predicted_fault?: string;
  type?: string;
  message: string;
  recommended_action: string;
  acknowledged: boolean;
}

export interface WebSocketPayload {
  type: 'TELEMETRY_UPDATE';
  data: ConditionResult;
  alert: Alert | null;
}

export interface SimulatorStatus {
  is_running: boolean;
  scenario: string;
  machine_id: string;
  interval: number;
  total_generated: number;
}

export interface SimulatorStartOptions {
  scenario?: string;
  machine_id?: string;
  steps?: number;
  interval?: number;
}

export interface ChartDataPoint {
  time: string;
  [key: string]: string | number;
}
