{{- if .Values.namespace.create -}}
apiVersion: v1
kind: Namespace
metadata:
  name: {{ .Values.namespace.name }}
  labels:
    app: cosmic-watch
---
{{- end }}

apiVersion: v1
kind: ConfigMap
metadata:
  name: cosmic-watch-config
  namespace: {{ .Values.namespace.name }}
  labels:
    app: cosmic-watch
data:
  VITE_API_URL: {{ .Values.frontend.env.VITE_API_URL | quote }}
  DEBUG: {{ .Values.backend.env.DEBUG | quote }}
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
  CORS_ORIGINS: |
    {{- range .Values.config.corsOrigins }}
    - {{ . }}
    {{- end }}
---

apiVersion: v1
kind: Secret
metadata:
  name: cosmic-watch-secrets
  namespace: {{ .Values.namespace.name }}
  labels:
    app: cosmic-watch
type: Opaque
stringData:
  DATABASE_URL: {{ .Values.backend.secrets.DATABASE_URL | quote }}
  REDIS_URL: {{ .Values.backend.secrets.REDIS_URL | quote }}
  SECRET_KEY: {{ .Values.backend.secrets.SECRET_KEY | quote }}
  NASA_API_KEY: {{ .Values.backend.secrets.NASA_API_KEY | quote }}
  OPENAI_API_KEY: {{ .Values.backend.secrets.OPENAI_API_KEY | quote }}
---

{{- if .Values.rbac.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ .Values.rbac.serviceAccountName }}
  namespace: {{ .Values.namespace.name }}
  labels:
    app: cosmic-watch
---

apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: cosmic-watch-role
  namespace: {{ .Values.namespace.name }}
  labels:
    app: cosmic-watch
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["get", "list", "watch"]
---

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: cosmic-watch-rolebinding
  namespace: {{ .Values.namespace.name }}
  labels:
    app: cosmic-watch
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: cosmic-watch-role
subjects:
- kind: ServiceAccount
  name: {{ .Values.rbac.serviceAccountName }}
  namespace: {{ .Values.namespace.name }}
{{- end }}
