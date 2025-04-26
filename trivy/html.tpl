{{- define "VulnerabilityTable" -}}
{{- $sortedVulns := sort .Vulnerabilities "Severity" "desc" -}}

<h3>Vulnerabilities</h3>
<table border="1" cellspacing="0" cellpadding="4">
    <thead>
        <tr>
            <th>Severity</th>
            <th>Package</th>
            <th>Installed Version</th>
            <th>Fixed Version</th>
            <th>Title</th>
            <th>References</th>
        </tr>
    </thead>
    <tbody>
    {{- range $sortedVulns }}
        <tr>
            <td>{{ .Severity }}</td>
            <td>{{ .PkgName }}</td>
            <td>{{ .InstalledVersion }}</td>
            <td>{{ .FixedVersion }}</td>
            <td>{{ .Title }}</td>
            <td>
                {{- range .References }}
                    <a href="{{ . }}">{{ . }}</a><br/>
                {{- end }}
            </td>
        </tr>
    {{- end }}
    </tbody>
</table>
{{- end -}}
