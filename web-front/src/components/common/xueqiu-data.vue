<template>
<div class="xueqiu_data">
  <p v-if="stockcode.length > 5">
    <label>机构评级综合得分：<strong>{{gradeScore}}</strong></label>
  </p>
  <div class="chart">
    <IEcharts :option="line_option" :loading="loading" @ready="onReady" theme="macarons" ></IEcharts>
  </div>
</div>
</template>

<script>
import HTTP from "@/core/fetch"
import IEcharts    from 'vue-echarts-v3/src/lite.vue'
import 'echarts/lib/component/title'
import 'echarts/lib/chart/line'
import 'echarts/lib/chart/bar'
import 'echarts/lib/component/legend'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/toolbox'
import 'echarts/theme/macarons'
import ChartHelper from '@/core/chartHelper'
export default {
  name: 'xueqiu-data',
  props: {
    stockcode: {
      type: String,
      required: true,
      default: ""
    },
  },
  data () {
    return {
      gradeScore: undefined,
      loading: false,
      eChartsIns: null,
      line_option: {},
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
      if(this.stockcode === '') {
        return
      }
      if(this.eChartsIns) {
        this.eChartsIns.clear()
      }
      const url = `/hkmainland/xueqiu_data?stockcode=${this.stockcode}`
      HTTP.get(url).then((dt) => {
        this.gradeScore = dt.data.score
        let xData = dt.data.xData
        let ydata1 = dt.data.yLineData1
        let ydata2 = dt.data.yLineData2 

        this.line_option = ChartHelper.buildXueqiuChart(this.stockcode, xData, ydata1, ydata2)
      })
    }
  },
  watch : {
    stockcode () {
      this.loadData()
    }
  },
   components: { IEcharts }
}
</script>

<style lang='scss' scoped>
strong {
  font-size: 150%;
  color: #EB6062;
}
.chart {
  height: 400px;
  width: 100%;
  margin: 0px 0px 0px -10px;
  padding: 5px;
}
</style>

