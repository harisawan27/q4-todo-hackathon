{{/*
Expand the name of the chart.
*/}}
{{- define "donekaro.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "donekaro.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Chart label
*/}}
{{- define "donekaro.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "donekaro.labels" -}}
helm.sh/chart: {{ include "donekaro.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: donekaro
{{- end }}

{{/*
Selector labels for a specific component
*/}}
{{- define "donekaro.selectorLabels" -}}
app.kubernetes.io/name: {{ .component }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Dapr annotations
*/}}
{{- define "donekaro.daprAnnotations" -}}
dapr.io/enabled: {{ .enabled | quote }}
dapr.io/app-id: {{ .appId | quote }}
dapr.io/app-port: {{ .appPort | quote }}
dapr.io/app-protocol: "http"
dapr.io/enable-api-logging: "true"
{{- end }}
