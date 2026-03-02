import api from './index'

export const paymentApi = {
  async createOrder(data) {
    return api.post('/payment/create', data)
  },

  async getOrders() {
    return api.get('/payment/orders')
  },

  async getProducts() {
    return api.get('/payment/products')
  }
}
