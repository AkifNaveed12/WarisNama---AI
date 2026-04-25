import { create } from 'zustand'

const useStore = create((set) => ({
  calculationResult: null,
  setCalculationResult: (result) => set({ calculationResult: result }),
  clearResult: () => set({ calculationResult: null }),
}))

export default useStore