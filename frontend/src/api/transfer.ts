import { type MaybeRefOrGetter, toValue } from 'vue'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { api, apiDownload } from './client'
import { saveBlob } from '@/utils/download'
import type { ExportFormat, ImportJobOut, ImportSource, ImportStartOut } from '@/types'

export async function downloadExportRequest(format: ExportFormat) {
  const { blob, filename } = await apiDownload('/users/me/export', { query: { format } })
  saveBlob(blob, filename ?? `kfdu-verilerim.${format}`)
}

export function useDownloadExport() {
  return useMutation({ mutationFn: downloadExportRequest })
}

export function startImportRequest(source: ImportSource, file: File) {
  const form = new FormData()
  form.append('source', source)
  form.append('file', file)
  return api<ImportStartOut>('/users/me/import', { method: 'POST', body: form })
}

export function useStartImport() {
  return useMutation({
    mutationFn: ({ source, file }: { source: ImportSource; file: File }) => startImportRequest(source, file),
  })
}

export function getImportJobRequest(jobId: number) {
  return api<ImportJobOut>(`/users/me/import/${jobId}`)
}

export function isImportActive(job: ImportJobOut | undefined): boolean {
  return job?.status === 'pending' || job?.status === 'running'
}

const IMPORT_POLL_MS = 1500

export function useImportJob(jobId: MaybeRefOrGetter<number | null>) {
  return useQuery(() => ({
    queryKey: ['import-job', toValue(jobId)],
    queryFn: () => getImportJobRequest(toValue(jobId) as number),
    enabled: toValue(jobId) !== null,
    // İş sürdükçe ilerleme için yoklanır, bitince durur
    refetchInterval: (query: { state: { data: ImportJobOut | undefined } }) =>
      isImportActive(query.state.data) ? IMPORT_POLL_MS : false,
    retry: false,
  }))
}

/** İçe aktarma kütüphaneyi, istatistikleri, rozetleri ve kartlardaki durumları değiştirir: hepsi tazelenir. */
export function useRefreshAfterImport() {
  const queryClient = useQueryClient()
  return () => queryClient.invalidateQueries({ predicate: (query) => query.queryKey[0] !== 'import-job' })
}
