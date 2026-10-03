import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { nextTick, type Ref } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import type { ImportJobOut } from '@/types'
import ImportCard from './ImportCard.vue'

const mocks = vi.hoisted(() => ({
  startImport: vi.fn<(vars: { source: string; file: File }) => Promise<{ job_id: number }>>(),
  refresh: vi.fn<() => Promise<void>>(),
  toastSuccess: vi.fn<(message: string) => void>(),
  toastError: vi.fn<(message: string) => void>(),
  jobData: null as Ref<ImportJobOut | undefined> | null,
}))

vi.mock('vue-sonner', () => ({ toast: { success: mocks.toastSuccess, error: mocks.toastError } }))

vi.mock('@/api/client', () => ({
  ApiError: class ApiError extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message)
    }
  },
}))

// Gerçek TanStack sorgusunun yerine: iş kimliği yokken veri de yoktur (enabled:false davranışı)
vi.mock('@/api/transfer', async () => {
  const { computed, ref, toValue } = await import('vue')
  mocks.jobData = ref<ImportJobOut | undefined>(undefined)
  const jobData = mocks.jobData
  return {
    isImportActive: (job?: ImportJobOut) => job?.status === 'pending' || job?.status === 'running',
    useImportJob: (jobId: Ref<number | null>) => ({
      data: computed(() => (toValue(jobId) === null ? undefined : jobData.value)),
      error: ref(null),
      isError: ref(false),
      refetch: vi.fn<() => Promise<void>>(),
    }),
    useStartImport: () => ({ mutateAsync: mocks.startImport, isPending: ref(false) }),
    useRefreshAfterImport: () => mocks.refresh,
  }
})

const STORAGE_KEY = 'kfdu:import-job:goodreads'

// useLocalStorage aynı anahtarlı örnekleri senkronlar; önceki testin kartı bağlı kalırsa o da tepki verir
enableAutoUnmount(afterEach)

function makeJob(overrides: Partial<ImportJobOut>): ImportJobOut {
  return {
    id: 7,
    source: 'goodreads',
    status: 'pending',
    total: 0,
    processed: 0,
    matched: 0,
    report: { file_kind: 'goodreads_library', unmatched: [] },
    error: null,
    created_at: '2026-10-04T10:00:00Z',
    finished_at: null,
    ...overrides,
  }
}

function mountCard(source: 'goodreads' | 'letterboxd' = 'goodreads') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:path(.*)*', component: { template: '<div />' } }],
  })
  return mount(ImportCard, {
    props: { source },
    global: { plugins: [createPinia(), router] },
  })
}

async function selectFile(wrapper: ReturnType<typeof mountCard>, file: File) {
  const input = wrapper.find('input[type="file"]')
  Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
  await input.trigger('change')
  await flushPromises()
}

describe('ImportCard', () => {
  beforeEach(() => {
    localStorage.clear()
    mocks.jobData!.value = undefined
    mocks.startImport.mockReset()
    mocks.refresh.mockReset()
    mocks.toastSuccess.mockReset()
    mocks.toastError.mockReset()
  })

  it('ZIP ya da 5 MB üstü dosyayı yüklemeden açıklamayla reddeder', async () => {
    const wrapper = mountCard()

    await selectFile(wrapper, new File(['PK'], 'goodreads.zip'))
    expect(mocks.toastError).toHaveBeenLastCalledWith('ZIP dosyasını açıp içindeki CSV dosyasını seç')

    await selectFile(wrapper, new File([new Uint8Array(5 * 1024 * 1024 + 1)], 'buyuk.csv'))
    expect(mocks.toastError).toHaveBeenLastCalledWith('Dosya en fazla 5 MB olabilir')

    expect(mocks.startImport).not.toHaveBeenCalled()
  })

  it('Letterboxd kartı ZIP’i doğrudan kabul eder; diğer uzantıları reddeder', async () => {
    mocks.startImport.mockResolvedValue({ job_id: 9 })
    const wrapper = mountCard('letterboxd')
    expect(wrapper.find('input[type="file"]').attributes('accept')).toContain('.zip')

    await selectFile(wrapper, new File(['x'], 'letterboxd-export.txt'))
    expect(mocks.toastError).toHaveBeenLastCalledWith('Dışa aktarılan .zip ya da .csv dosyasını seç')
    expect(mocks.startImport).not.toHaveBeenCalled()

    const zip = new File(['PK'], 'letterboxd-export-2026.zip')
    await selectFile(wrapper, zip)
    expect(mocks.startImport).toHaveBeenCalledWith({ source: 'letterboxd', file: zip })
  })

  it('dosya seçilince işi başlatır, ilerlemeyi gösterir, bitince verileri tazeleyip sonucu raporlar', async () => {
    mocks.startImport.mockResolvedValue({ job_id: 7 })
    const wrapper = mountCard()
    const file = new File(['Title,Exclusive Shelf\nKitap,read\n'], 'goodreads_library_export.csv')

    await selectFile(wrapper, file)
    expect(mocks.startImport).toHaveBeenCalledWith({ source: 'goodreads', file })
    expect(localStorage.getItem(STORAGE_KEY)).toBe('7')

    mocks.jobData!.value = makeJob({ status: 'running', processed: 10, total: 40 })
    await nextTick()
    expect(wrapper.find('[role="progressbar"]').attributes('aria-valuenow')).toBe('10')
    expect(wrapper.text()).toContain('10 / 40')

    mocks.jobData!.value = makeJob({
      status: 'done',
      processed: 40,
      total: 40,
      matched: 38,
      report: { file_kind: 'goodreads_library', unmatched: ['Kitap A — Yazar', 'Kitap B — Yazar'] },
    })
    await nextTick()
    expect(mocks.refresh).toHaveBeenCalledTimes(1)
    expect(mocks.toastSuccess).toHaveBeenCalledWith('İçe aktarma tamamlandı: 38/40 eşleşti')
    expect(wrapper.text()).toContain('38 / 40')
    expect(wrapper.text()).toContain('Eşleşmeyenler (2)')
    expect(wrapper.text()).toContain('Kitap B — Yazar')
    // Kitaplar içe aktarıldı: bağlantı varsayılan film rafına değil "Okuduklarım"a iner
    expect(wrapper.find('a').attributes('href')).toContain('raf=okunan')
  })

  it('sayfaya dönüldüğünde biten işin sonucunu gösterir ama bildirimi tekrarlamaz; "Başka dosya yükle" sıfırlar', async () => {
    localStorage.setItem(STORAGE_KEY, '7')
    mocks.jobData!.value = makeJob({ status: 'done', processed: 3, total: 3, matched: 3 })
    const wrapper = mountCard()
    await nextTick()

    expect(wrapper.text()).toContain('içerik eşleşti')
    expect(mocks.toastSuccess).not.toHaveBeenCalled()
    expect(mocks.refresh).not.toHaveBeenCalled()

    const resetButton = wrapper.findAll('button').find((b) => b.text().includes('Başka dosya yükle'))
    await resetButton!.trigger('click')
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull()
    expect(wrapper.text()).toContain('CSV dosyası seç')
  })

  it('iş başarısız biterse hatayı gösterir ve yine de verileri tazeler (eşleşenler eklenmiş olabilir)', async () => {
    mocks.startImport.mockResolvedValue({ job_id: 7 })
    const wrapper = mountCard()
    await selectFile(wrapper, new File(['x'], 'goodreads_library_export.csv'))

    mocks.jobData!.value = makeJob({
      status: 'failed',
      processed: 5,
      total: 20,
      matched: 2,
      error: 'Film/kitap veri kaynağı şu anda yanıt vermiyor.',
    })
    await nextTick()
    expect(mocks.refresh).toHaveBeenCalledTimes(1)
    expect(mocks.toastError).toHaveBeenCalledWith('İçe aktarma tamamlanamadı')
    expect(wrapper.text()).toContain('yanıt vermiyor')
    expect(wrapper.text()).toContain('5 / 20 satır işlendi, 2 içerik eklendi.')
  })
})
