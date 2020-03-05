import Numeral from 'numeral'
const discount = {"1": "1", "3": "0.95", "6": "0.88", "12": "0.83"}
export default class Order {
  static calculateFee (monthes) {
    const monthlyFee = 20
    let fee = 0
    let realFee = 0
    if(monthes === '12') {
      [fee, realFee] = [200, 240]
    } else {
      if(monthes === '1') {
        [fee, realFee] = [monthlyFee, 40]
      } else {
        [fee, realFee] = [Numeral((monthlyFee * parseFloat(discount[monthes])) * parseInt(monthes)).format("0.0"), Numeral(monthlyFee * parseInt(monthes)).format("0.0")]
      }
    }
    return [fee, realFee]
  }
}