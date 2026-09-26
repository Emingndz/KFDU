import { reactive } from 'vue'

export interface ConfirmOptions {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
}

interface ConfirmState extends Required<ConfirmOptions> {
  open: boolean
}

const state = reactive<ConfirmState>({
  open: false,
  title: '',
  message: '',
  confirmText: 'Onayla',
  cancelText: 'Vazgeç',
  danger: false,
})

let resolver: ((value: boolean) => void) | null = null

export function useConfirm() {
  function confirm(options: ConfirmOptions): Promise<boolean> {
    resolver?.(false)
    Object.assign(state, {
      confirmText: 'Onayla',
      cancelText: 'Vazgeç',
      danger: false,
      ...options,
      open: true,
    })
    return new Promise((resolve) => {
      resolver = resolve
    })
  }

  function resolve(value: boolean) {
    state.open = false
    resolver?.(value)
    resolver = null
  }

  return { state, confirm, resolve }
}
