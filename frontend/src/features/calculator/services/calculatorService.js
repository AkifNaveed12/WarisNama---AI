// import { endpoints } from '../../../services/endpoints'

// export const calculateShares = async (data) => {
//   const response = await endpoints.calculateShares(data)
//   return response.data
// }

// export const calculateTax = async (data) => {
//   const response = await endpoints.calculateTax(data)
//   return response.data
// }

// export const detectDisputes = async (flags) => {
//   const response = await endpoints.detectDisputes(flags)
//   return response.data
// }

// export const generateShareCertificate = async (data) => {
//   const response = await endpoints.generateShareCertificate(data)
//   return response.data
// }




// import { endpoints } from '../../../services/endpoints'

// export const calculateShares = async (data) => {
//   const response = await endpoints.calculateShares(data)
//   return response.data
// }

// export const parseNLP = async (text) => {
//   const response = await endpoints.parseNLP(text)
//   return response.data
// }

// export const detectDisputes = async (flags) => {
//   const response = await endpoints.detectDisputes(flags)
//   return response.data
// }

// export const calculateTax = async (data) => {
//   const response = await endpoints.calculateTax(data)
//   return response.data
// }

// export const getProcessSteps = async (hasMinor, hasDispute, isSelling) => {
//   const response = await endpoints.getProcessSteps(hasMinor, hasDispute, isSelling)
//   return response.data
// }

// export const generateShareCertificate = async (data) => {
//   const response = await endpoints.generateShareCertificate(data)
//   return response.data
// }



import { endpoints } from '../../../services/endpoints'

export const calculateShares = async (data) => {
  const response = await endpoints.calculateShares(data)
  return response.data
}

export const parseNLP = async (text) => {
  const response = await endpoints.parseNLP(text)
  return response.data
}

export const detectDisputes = async (flags) => {
  const response = await endpoints.detectDisputes(flags)
  return response.data
}

export const calculateTax = async (data) => {
  const response = await endpoints.calculateTax(data)
  return response.data
}

export const getProcessSteps = async (hasMinor, hasDispute, isSelling) => {
  const response = await endpoints.getProcessSteps(hasMinor, hasDispute, isSelling)
  return response.data
}

export const generateShareCertificate = async (data) => {
  const response = await endpoints.generateShareCertificate(data)
  return response.data
}