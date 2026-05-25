import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

/**
 * 通过 ResizeObserver 监听容器高度，返回可直接传给 el-table :height 的响应式值。
 * 支持 v-if/标签页内延迟挂载场景（ref 在 onMounted 之后才赋值）。
 * @param {import('vue').Ref<HTMLElement|null>} containerRef - 表格直接父容器的 ref
 * @param {number} subtract - 需要额外减去的像素（例如卡片内其他固定高度区域）
 */
export function useTableHeight(containerRef, subtract = 0) {
  const tableHeight = ref(400)

  let ro = null

  function measure() {
    if (containerRef.value) {
      tableHeight.value = Math.max(180, containerRef.value.clientHeight - subtract)
    }
  }

  onMounted(async () => {
    await nextTick()
    ro = new ResizeObserver(measure)
    if (containerRef.value) {
      ro.observe(containerRef.value)
      measure()
    }
  })

  // 支持 v-if / el-tabs 标签页延迟渲染：ref 从 null 变为元素时自动开始监听
  watch(containerRef, (el) => {
    if (el && ro) {
      ro.observe(el)
      measure()
    }
  })

  onBeforeUnmount(() => {
    ro?.disconnect()
  })

  return tableHeight
}
