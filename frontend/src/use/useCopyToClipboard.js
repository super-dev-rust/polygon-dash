import { ElNotification } from 'element-plus'

export function useCopyToClipboard() {
  async function copyToClipboard(copyText) {
    try {
      await navigator.clipboard.writeText(copyText)
      ElNotification.success({
        title: 'Copied successfully!',
        position: 'top-right',
        zIndex: 100000
      })
    } catch (err) {
      ElNotification.error({
        title: 'Copy failed!',
        duration: 0,
        position: 'top-right',
        zIndex: 100000,
        message: err,
      })
    }
  }

  return {
    copyToClipboard,
  }
}

export default useCopyToClipboard
