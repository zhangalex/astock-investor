<template>
<div class="flow_chart">
  <div class="row">
    <div class="col-md-12 splitter">
      <el-tabs type="card">
        <el-tab-pane label="持有变化曲线">
          <div class="chart">
            <div class="box">
              <IEcharts :option="line_option" :loading="loading" @ready="onReady" theme="macarons"></IEcharts>
            </div>
            <div class="dateRangeSelector"><el-date-picker @change="dateRangeChanged" v-model="chartDateRange" value-format="yyyy-MM-dd" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"></el-date-picker></div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="境外市场参与者详情">
          <Wzholders :stockcode="code" :perPage="12"  v-if="code != null" :isLongColumn="1" />
        </el-tab-pane>
      </el-tabs>
     
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
import Wzholders    from '@/components/common/wz-holders'
export default {
  name: 'flow-chart',
  props: {
    hkcode: {
      type: String,
      required: true,
      default: null
    },
    code: {
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
      const url = `/hkmainland/north_chart?hkcode=${this.hkcode}`
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
        const url = `/hkmainland/north_chart?hkcode=${this.hkcode}&start=${start}&end=${end}` 
        HTTP.get(url).then((dt) => {
          this.line_option = ChartHelper.buildFlowChart(dt.data)
        })

      }
    }
  },
  components: { IEcharts, Wzholders },
  watch : {
    code () {
      this.loadData()
    }
  }
}
</script>
<style lang='scss'>
.el-input__inner {
  font-size: 12px;
  height: 36px;
}
.el-dialog__body {
  padding: 10px 20px;
}
.el-dialog {
  margin-top: 10vh;
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

