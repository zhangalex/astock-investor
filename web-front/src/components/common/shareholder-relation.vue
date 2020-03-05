<template>
<div class="shareholder-relation">
  <div class="row">
    <div class="col-md-12">
      <div class="chart" v-if="relationOptions != null">
        <IEcharts :option="relationOptions" :loading="loading" @ready="onReady" theme="macarons"></IEcharts>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import IEcharts    from 'vue-echarts-v3/src/lite.vue'
import 'echarts/lib/component/title'
import 'echarts/lib/chart/line'
import 'echarts/lib/chart/bar'
import 'echarts/lib/component/legend'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/toolbox'
import 'echarts/theme/macarons'
import HTTP from "@/core/fetch"
import ChartHelper from '@/core/chartHelper'
export default {
  name: 'shareholder-relation',
  props: {
    holderName: {
      type: String,
      required: true,
      default: null
    },
    holderCategory: {
      type: Number,
      required: true,
      default: 0

    }
  },
  data () {
    return {
      loading: false,
      relationOptions: null,
      eChartsIns: null
    }
  },
  methods: {
    loadData () {
      if(this.holderName != null) {
        const url = `/hkmainland/shareholder_relation?name=${this.holderName}&category=${this.holderCategory}`
        HTTP.get(url).then(dt => {
          const data = dt.data.list
          console.log(data)
          const categories = [
            {
              name: '股东-公司关系',
              keyword: {},
              base: '股东-公司关系'
            }
          ]
          let nodes = [{name: this.holderName, value:0, symbolSize: 1, category: 0, itemStyle: {normal: {color: 'grey'}}}]
          let links = []
          data.forEach((item, i) => {
           nodes.push({name: item.name, value: item.stockPercent, symbolSize: item.stockPercent, category: 0, itemStyle: {normal: {color: '#017E14'}}}) 
           links.push({source: 0, target: i + 1})
          })
          this.relationOptions = ChartHelper.buildRelationChart('股东-公司 关系图', categories, nodes, links)
        })
      }
    },
    onReady (ins) {
      this.eChartsIns = ins
    }
  },
  mounted () {
    this.$watch(vm => [vm.holderName, vm.holderCategory].join(), val => {
      console.log('change.....')
      this.loadData()
    })
    this.loadData()
  },
  components: { IEcharts }
  // watch: {
  //   holderName () {
  //     this.loadData()
  //   },
  //   holderType () {

  //   }
  // }
}
</script>
<style lang='scss'>
.el-dialog__body {
  padding: 0px 20px;
}
</style>
<style lang='scss' scoped>
.chart {
  // background-color: #F8F8F8;
  min-height: 350px;
  height: 600px;
  margin: 0px 0px 0px -10px;
  // border: solid 1px silver;
  padding: 5px;
}
</style>
