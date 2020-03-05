<template>
<div class="flow_chart">
  <div class="row">
    <div class="col-md-12 splitter">
      <div class="chart">
        <div class="box">
          <IEcharts :option="line_option" :loading="loading" @ready="onReady" theme="macarons"></IEcharts>
        </div>
        <div class="dateRangeSelector"><el-date-picker @change="dateRangeChanged" v-model="chartDateRange" value-format="yyyy-MM-dd" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"></el-date-picker></div>
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
  name: 'holderhold-chart',
  props: {
    code: {
      type: String,
      required: true,
      default: null
    },
    stockcode: {
      type: String,
      required: true,
      default: null
    }
  },
  data () {
    return {
      line_option: {},
      loading: false,
      eChartsIns: null,
      chartDateRange: ['', '']
    }
  },
  mounted () {
    this.loadData()
  },
  methods: {
    onReady (ins) {
      this.eChartsIns = ins
    },
    loadData () {
      if(this.code === null) {
        return
      }
      if(this.eChartsIns) {
        this.eChartsIns.clear()
      }
      const url = `/hkmainland/holders_chart?code=${this.code}&stockcode=${this.stockcode}`
      HTTP.get(url).then((dt) => {
        this.line_option = ChartHelper.buildFlowChart(dt.data)
        this.chartDateRange = ['', '']
        this.chartDateRange[0] = dt.data.start
        this.chartDateRange[1] = dt.data.end
      })
    },
    dateRangeChanged () {
      // console.log(this.chartDateRange)
      if(this.eChartsIns) {
        this.eChartsIns.clear()
      }
      if(this.chartDateRange != null && this.chartDateRange[0] && this.chartDateRange[1]) {
        let [start, end] = this.chartDateRange
        const url = `/hkmainland/holders_chart?code=${this.code}&stockcode=${this.stockcode}&start=${start}&end=${end}` 
        HTTP.get(url).then((dt) => {
          this.line_option = ChartHelper.buildFlowChart(dt.data)
        })

      }
    }
  },
  components: { IEcharts },
  watch : {
    code () {
      this.loadData()
    },
    stockcode () {
      this.loadData()
    }
  }
}
</script>
<style lang='scss'>
.el-dialog__body {
  padding: 10px 20px;
}
</style>
<style lang='scss' scoped>

.chart {
  // background-color: #F8F8F8;
  min-height: 300px;
  margin: 0px 0px 0px -10px;
  // border: solid 1px silver;
  padding: 5px;
}
.chart .box {
  height: 480px;
}
.chart .dateRangeSelector {
  margin-top: 10px;
  text-align: center;
}
.col-md-12 {
  padding-right: 1px;
}
</style>

