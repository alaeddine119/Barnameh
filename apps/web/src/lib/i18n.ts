export type Language = 'en' | 'it';

export interface Translations {
  // Header
  dashboard: string;
  
  // Home Page
  title: string;
  subtitle: string;
  operationalAnalytics: string;
  
  // KPI Dashboard
  totalProduction: string;
  resourceUtilization: string;
  attendanceRate: string;
  equipmentHealth: string;
  units: string;
  
  // Recommendations
  aiRecommendations: string;
  recommendations: string;
  loading: string;
  errorLoadingRecommendations: string;
  noRecommendations: string;
  lastUpdated: string;
  whyThisMatters: string;
  expectedImpact: string;
  overallStatus: string;
  optimal: string;
  avgDailyOutput: string;
  avgDailyDowntime: string;
  daysAnalyzed: string;
  highPriority: string;
  
  // Demand Forecast
  demandForecast: string;
  for: string;
  forecast: string;
  actual: string;
  confidence: string;
  nextDays: string;
  avgDailyDemand: string;
  peakDemand: string;
  minDemand: string;
  noForecastData: string;
  
  // Anomaly Alerts
  anomalyAlerts: string;
  noAnomalies: string;
  severity: string;
  high: string;
  medium: string;
  low: string;
  critical: string;
  warning: string;
  info: string;
  performanceDegradation: string;
  performanceDegradationDetected: string;
  systemFailureRisk: string;
  resourceBottleneckPredicted: string;
  probability: string;
  in: string;
  confidenceInterval: string;
  predictedDemand: string;
  blueLine: string;
  shadedArea: string;
  
  // Resource Utilization
  resourceUtilization7Days: string;
  utilization: string;
  efficiency: string;
  downtime: string;
  minutes: string;
  noResourceData: string;
  
  // Production & Revenue
  productionRevenueTrends: string;
  production: string;
  revenue: string;
  totalProduced: string;
  totalRevenue: string;
  avgDailyProduction: string;
  avgDailyRevenue: string;
  noRevenueData: string;
  noProductionData: string;
  
  // Attendance Trends
  attendanceTrends: string;
  attendance: string;
  rate: string;
  present: string;
  absent: string;
  avgAttendance: string;
  totalPresent: string;
  totalAbsent: string;
  presentToday: string;
  absentToday: string;
  noAttendanceData: string;
  
  // AI Chat
  aiChatAssistant: string;
  askQuestion: string;
  typeMessage: string;
  send: string;
  thinking: string;
  errorSendingMessage: string;
  
  // Common
  error: string;
  refresh: string;
  close: string;
  show: string;
  hide: string;
  more: string;
  less: string;
  live: string;
  updated: string;
  days: string;
  keyPerformanceIndicators: string;
  realTimeMetrics: string;
  last: string;
}

export const translations: Record<Language, Translations> = {
  en: {
    // Header
    dashboard: 'Dashboard',
    
    // Home Page
    title: 'BarnamehAI',
    subtitle: 'Real-time predictions and insights for operational efficiency',
    operationalAnalytics: 'Operational Analytics',
    
    // KPI Dashboard
    totalProduction: 'Total Production',
    resourceUtilization: 'Resource Utilization',
    attendanceRate: 'Attendance Rate',
    equipmentHealth: 'Equipment Health',
    units: 'units',
    
    // Recommendations
    aiRecommendations: 'AI Recommendations',
    recommendations: 'Recommendations',
    loading: 'Loading',
    errorLoadingRecommendations: 'Error loading recommendations',
    noRecommendations: 'No recommendations available',
    lastUpdated: 'Last updated',
    whyThisMatters: 'Why This Matters',
    expectedImpact: 'Expected Impact',
    overallStatus: 'Overall Status',
    optimal: 'Optimal',
    avgDailyOutput: 'Avg Daily Output',
    avgDailyDowntime: 'Avg Daily Downtime',
    daysAnalyzed: 'Days Analyzed',
    highPriority: 'HIGH PRIORITY',
    
    // Demand Forecast
    demandForecast: 'Demand Forecast',
    for: 'for',
    forecast: 'Forecast',
    actual: 'Actual',
    confidence: 'Confidence',
    nextDays: 'Next 30 Days',
    avgDailyDemand: 'Avg Daily Demand',
    peakDemand: 'Peak Demand',
    minDemand: 'Min Demand',
    noForecastData: 'No forecast data available',
    
    // Anomaly Alerts
    anomalyAlerts: 'Anomaly Alerts',
    noAnomalies: 'No anomalies detected',
    severity: 'Severity',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
    critical: 'Critical',
    warning: 'Warning',
    info: 'Info',
    performanceDegradation: 'performance_degradation',
    performanceDegradationDetected: 'Performance Degradation Detected',
    systemFailureRisk: 'System Failure Risk',
    resourceBottleneckPredicted: 'Resource Bottleneck Predicted',
    probability: 'Probability',
    in: 'in',
    confidenceInterval: '95% confidence interval',
    predictedDemand: 'Predicted demand',
    blueLine: 'Blue line',
    shadedArea: 'Shaded area',
    
    // Resource Utilization
    resourceUtilization7Days: 'Resource Utilization (Last 7 Days)',
    utilization: 'Utilization',
    efficiency: 'Efficiency',
    downtime: 'Downtime',
    minutes: 'minutes',
    noResourceData: 'No resource data available',
    
    // Production & Revenue
    productionRevenueTrends: 'Production & Revenue Trends',
    production: 'Production',
    revenue: 'Revenue',
    totalProduced: 'Total Produced',
    totalRevenue: 'Total Revenue',
    avgDailyProduction: 'Avg Daily Production',
    avgDailyRevenue: 'Avg Daily Revenue',
    noRevenueData: 'No revenue data available',
    noProductionData: 'No production data available',
    
    // Attendance Trends
    attendanceTrends: 'Attendance Trends',
    attendance: 'Attendance',
    rate: 'Rate',
    present: 'Present',
    absent: 'Absent',
    avgAttendance: 'Avg Attendance',
    totalPresent: 'Total Present',
    totalAbsent: 'Total Absent',
    presentToday: 'Present Today',
    absentToday: 'Absent Today',
    noAttendanceData: 'No attendance data available',
    
    // AI Chat
    aiChatAssistant: 'AI Chat Assistant',
    askQuestion: 'Ask a question about your operations',
    typeMessage: 'Type your message...',
    send: 'Send',
    thinking: 'Thinking...',
    errorSendingMessage: 'Error sending message',
    
    // Common
    error: 'Error',
    refresh: 'Refresh',
    close: 'Close',
    show: 'Show',
    hide: 'Hide',
    more: 'More',
    less: 'Less',
    live: 'Live',
    updated: 'Updated',
    days: 'days',
    keyPerformanceIndicators: 'Key Performance Indicators',
    realTimeMetrics: 'Real-time metrics',
    last: 'Last',
  },
  it: {
    // Header
    dashboard: 'Cruscotto',
    
    // Home Page
    title: 'BarnamehAI',
    subtitle: 'Previsioni e approfondimenti in tempo reale per l\'efficienza operativa',
    operationalAnalytics: 'Analisi Operativa',
    
    // KPI Dashboard
    totalProduction: 'Produzione Totale',
    resourceUtilization: 'Utilizzo Risorse',
    attendanceRate: 'Tasso di Presenza',
    equipmentHealth: 'Salute Attrezzature',
    units: 'unità',
    
    // Recommendations
    aiRecommendations: 'Raccomandazioni IA',
    recommendations: 'Raccomandazioni',
    loading: 'Caricamento',
    errorLoadingRecommendations: 'Errore nel caricamento delle raccomandazioni',
    noRecommendations: 'Nessuna raccomandazione disponibile',
    lastUpdated: 'Ultimo aggiornamento',
    whyThisMatters: 'Perché è Importante',
    expectedImpact: 'Impatto Previsto',
    overallStatus: 'Stato Generale',
    optimal: 'Ottimale',
    avgDailyOutput: 'Produzione Media Giornaliera',
    avgDailyDowntime: 'Tempo di Inattività Medio',
    daysAnalyzed: 'Giorni Analizzati',
    highPriority: 'ALTA PRIORITÀ',
    
    // Demand Forecast
    demandForecast: 'Previsione Domanda',
    for: 'per',
    forecast: 'Previsione',
    actual: 'Effettivo',
    confidence: 'Confidenza',
    nextDays: 'Prossimi 30 Giorni',
    avgDailyDemand: 'Domanda Media Giornaliera',
    peakDemand: 'Domanda Massima',
    minDemand: 'Domanda Minima',
    noForecastData: 'Nessun dato di previsione disponibile',
    
    // Anomaly Alerts
    anomalyAlerts: 'Avvisi di Anomalia',
    noAnomalies: 'Nessuna anomalia rilevata',
    severity: 'Gravità',
    high: 'Alta',
    medium: 'Media',
    low: 'Bassa',
    critical: 'Critica',
    warning: 'Avviso',
    info: 'Info',
    performanceDegradation: 'degradazione_prestazioni',
    performanceDegradationDetected: 'Rilevata Degradazione delle Prestazioni',
    systemFailureRisk: 'Rischio di Guasto del Sistema',
    resourceBottleneckPredicted: 'Previsto Collo di Bottiglia delle Risorse',
    probability: 'Probabilità',
    in: 'tra',
    confidenceInterval: 'Intervallo di confidenza 95%',
    predictedDemand: 'Domanda prevista',
    blueLine: 'Linea blu',
    shadedArea: 'Area ombreggiata',
    
    // Resource Utilization
    resourceUtilization7Days: 'Utilizzo Risorse (Ultimi 7 Giorni)',
    utilization: 'Utilizzo',
    efficiency: 'Efficienza',
    downtime: 'Tempo di Inattività',
    minutes: 'minuti',
    noResourceData: 'Nessun dato risorsa disponibile',
    
    // Production & Revenue
    productionRevenueTrends: 'Tendenze Produzione e Ricavi',
    production: 'Produzione',
    revenue: 'Ricavi',
    totalProduced: 'Totale Prodotto',
    totalRevenue: 'Ricavi Totali',
    avgDailyProduction: 'Produzione Media Giornaliera',
    avgDailyRevenue: 'Ricavi Medi Giornalieri',
    noRevenueData: 'Nessun dato sui ricavi disponibile',
    noProductionData: 'Nessun dato di produzione disponibile',
    
    // Attendance Trends
    attendanceTrends: 'Tendenze Presenza',
    attendance: 'Presenza',
    rate: 'Tasso',
    present: 'Presente',
    absent: 'Assente',
    avgAttendance: 'Presenza Media',
    totalPresent: 'Totale Presenti',
    totalAbsent: 'Totale Assenti',
    presentToday: 'Presenti Oggi',
    absentToday: 'Assenti Oggi',
    noAttendanceData: 'Nessun dato di presenza disponibile',
    
    // AI Chat
    aiChatAssistant: 'Assistente Chat IA',
    askQuestion: 'Fai una domanda sulle tue operazioni',
    typeMessage: 'Scrivi il tuo messaggio...',
    send: 'Invia',
    thinking: 'Pensando...',
    errorSendingMessage: 'Errore nell\'invio del messaggio',
    
    // Common
    error: 'Errore',
    refresh: 'Aggiorna',
    close: 'Chiudi',
    show: 'Mostra',
    hide: 'Nascondi',
    more: 'Altro',
    less: 'Meno',
    live: 'Live',
    updated: 'Aggiornato',
    days: 'giorni',
    keyPerformanceIndicators: 'Indicatori Chiave di Prestazione',
    realTimeMetrics: 'Metriche in tempo reale',
    last: 'Ultimi',
  },
};
