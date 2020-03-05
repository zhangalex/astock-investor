<template>
<div class="calculator">
  <div class="row">
    <div class="col-md-4">
      <normal-frame title="加仓成本计算" width="100%">
        <el-form ref="form" :model="addCost" label-width="100px">
          <el-form-item label="当前成本：">
              <el-input v-model="addCost.currentPrice" placeholder="输入价格"></el-input>
           </el-form-item>
           <el-form-item label="当前持股数：">
              <el-input v-model="addCost.currentQuantity" placeholder="输入数量"></el-input>
           </el-form-item>
           <el-form-item label="加仓价格：">
              <el-input v-model="addCost.addPrice" placeholder="输入价格"></el-input>
           </el-form-item>
            <el-form-item label="加仓数量：">
              <el-input v-model="addCost.addQuantity" placeholder="输入数量"></el-input>
           </el-form-item>
           <el-form-item label="最终成本 =>">
              <div class="el-input result">{{addCostPrice}}</div>
           </el-form-item>
        </el-form>
      </normal-frame>
    </div>
    
    <div class="col-md-4">
      <normal-frame title="盈利目标计算" width="100%">
        <el-form ref="form" :model="profit" label-width="90px">
           <el-form-item label="盈利目标：">
              <el-input v-model="profit.target" placeholder="输入金额，单位：元"></el-input>
           </el-form-item>
           <el-form-item label="持股成本：">
              <el-input v-model="profit.costPrice" placeholder="输入价格"></el-input>
           </el-form-item>
           <el-form-item label="持股数：">
              <el-input v-model="profit.stockQuantity" placeholder="输入数量"></el-input>
           </el-form-item>
           <el-form-item label="出售价 =>">
              <div class="el-input result">{{soldOutPrice}}</div>
           </el-form-item>
           <!-- <el-form-item>
            <el-button type="primary" @click="saveProfit">保存</el-button>
           </el-form-item> -->
        </el-form>

      </normal-frame>
    </div>

    <div class="col-md-4">

    </div>
  </div>
</div>
</template>

<script>
import NormalFrame from '@/components/common/normal-frame'
import Math from 'mathjs'
import Store from '@/core/localStore.js'
export default {
  name: 'calculator',
  data () {
    return {
      addCost: {
        currentPrice: null,
        currentQuantity: null,
        addPrice: null,
        addQuantity: null
      },
      profit: {
        target: null,
        costPrice: null,
        stockQuantity: null,
        soldPrice: null
      }
    }
    
  },
  mounted () {
    // this.fetchStock('601006')
  },
  methods: {
    // fetchStock (code) {
    //   this.$http.get(`/api/fetch_stock?code=${code}`).then(dt => {
    //     let data = dt.data.split('=')[1]
    //     console.log(data)
    //     let items = data.split(',')
    //     let currentPrice =  items[3]
    //     console.log(currentPrice)
    //   })
    // },
    saveProfit () {
      // let code = '601006'
      // let dt = await(this.$http.get(`/api/fetch_stock?code=${code}`))
      // console.log(dt)
    }
  },
  computed: {
    soldOutPrice () {
      let costPrice = parseFloat(this.profit.costPrice)
      let target    = parseFloat(this.profit.target)
      let quantity  = parseFloat(this.profit.stockQuantity)

      if(costPrice > 0 && target > 0 && quantity > 0) {
        return `￥${Math.round(costPrice + (target / quantity), 2)}`
      } else {
        return null
      }
    },
    addCostPrice () {
      let currentPrice = parseFloat(this.addCost.currentPrice)
      let currentQuantity = parseFloat(this.addCost.currentQuantity)
      let addPrice = parseFloat(this.addCost.addPrice)
      let addQuantity = parseFloat(this.addCost.addQuantity)
      if(!isNaN(currentPrice) && !isNaN(currentQuantity) && !isNaN(addPrice) && !isNaN(addQuantity)) {
        let targetPrice = ((currentPrice * currentQuantity) + (addPrice * addQuantity)) / (currentQuantity + addQuantity)
        return Math.round(targetPrice, 2)
      } else {
        return null
      }
    }
  },
  components: { NormalFrame }
}
</script>
<style lang='scss'>
@import 'src/assets/overrite_element';
.calculator {
  margin: 10px 0px;
}
.result {
  text-align: left;
  font-size: 14px;
  font-weight: 400;
  color: red;
}
.el-form-item__label {
  font-size: 13px;
}
.el-input__inner {
  font-size: 13px;
}
</style>
