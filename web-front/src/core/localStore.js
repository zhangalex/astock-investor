const profitItemKey = 'profit_item_key'

export default class profitStore {
  static _setItems (items) {
    localStorage.setItem(profitItemKey, JSON.stringify(items))
  }
  static _getItems () {
    const items = localStorage.getItem(profitItemKey)
    if (items) {
        return JSON.parse(items)
    } else {
        return []
    }
  }
  static addItem (item) {
    if (item) {
        let items = this._getItems()
        let existedItem = items.find(it => it.code === item.code)
        if (!existedItem) {
            items.push(item)
            this._setItems(items)
        }
    }
  }
  static removeItem (item) {
    if (item) {
        let items = this._getItems()
        if (items) {
            items = items.filter(it => it.code !== item.code)
            this._setItems(items)
        }

    }
  }
  static removeAll () {
    localStorage.removeItem(profitItemKey)
  }
  static getItems () {
    return this._getItems()
  }
}
