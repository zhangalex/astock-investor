<template>
  <div>
    <div class="row">
      <!-- <div class="col-md-6">
        <normal-frame title="港股通-买入卖出-数量统计"  width="100%">
          	<div class="map" v-if="hkbs_count_chart_options != null">
							<IEcharts :option="hkbs_count_chart_options" theme="macarons"></IECharts>
						</div>
        </normal-frame>
        <div class="chartTypeSelector">
          <el-radio-group v-model="hkcountChartType"  size="mini" @change="hkchartChange">
          <el-radio-button label="Line"></el-radio-button>
          <el-radio-button label="Bar"></el-radio-button>
          </el-radio-group>
        </div>
      </div> -->
      <div class="col-md-12">
        <normal-frame title="港股通-流入流出-净额统计"  width="100%">
          	<div class="map" v-if="hkbs_amount_chart_options != null">
							<IEcharts :option="hkbs_amount_chart_options" theme="infographic"></IECharts>
						</div>
        </normal-frame>
        <div class="chartTypeSelector">
          <el-radio-group v-model="hkamountChartType"  size="mini" @change="hkchartChange">
          <el-radio-button label="Line"></el-radio-button>
          <el-radio-button label="Bar"></el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </div>
    <div class="row" style="margin-top:15px">
      <div class="col-md-6">
        <normal-frame title="港股通-连续买入" :lastUpdate="hkLastDate" width="100%">
          <vue-table :url="hkbuyDataUrl"  className="table is-striped" :showPager="true" @onLastUpdated="setHkUpdated" @onRowSelected="stockSelected"></vue-table> 
        </normal-frame>
        <div class="block">
          <vueSlider v-model="hkbuyCDays" :min="0" :max="30" :interval="1"  :piecewise="true" tooltip="hover"  @callback="hksliderBuyChg"></vueSlider>
        </div>
        
      </div>
      <div class="col-md-6">
        <normal-frame title="港股通-连续卖出" :lastUpdate="hkLastDate" width="100%">
          <vue-table :url="hksoldDataUrl"  className="table is-striped" :showPager="true" @onLastUpdated="setHkUpdated" @onRowSelected="stockSelected"></vue-table> 
        </normal-frame>
        <div class="block">
          <vueSlider v-model="hksoldCDays" :min="0" :max="30" :interval="1"  :piecewise="true" tooltip="hover"  @callback="hksliderSoldChg"></vueSlider>
        </div>
      </div>
    </div>
    <el-dialog
      title=""
      :visible.sync="dialogVisible"
      width="65%">
      <flow-chart :hkcode="selectedHkCode" :code="selectedCode"></flow-chart>
    </el-dialog>
  </div>
</template>

<script>
import vueSlider from 'vue-slider-component'
import NormalFrame from '@/components/common/normal-frame'
import VueTable    from '@/components/common/vue-table'
import FlowChart   from '@/components/common/flow-chart'
import IEcharts from 'vue-echarts-v3/src/lite.vue'
import 'echarts/theme/infographic'
import 'echarts/theme/macarons'
import moment from 'moment'
import ChartHelper from '@/core/chartHelper'
import HTTP from "@/core/fetch"
export default {
  name: 'GgtBuyAndSold',
  data () {
    return {
      hkStatsData: null,
      hkLastDate: null,
      hkbs_count_chart_options: null,
      hkcountChartType: null,
      hkbs_amount_chart_options: null,
      hkamountChartType: null,
      hkcountChartType: 'Line',
      hkamountChartType: 'Line',
      hkbuyDataUrl: '/hkmainland/flow_continue?direction=buy&source=hk',
      hksoldDataUrl: '/hkmainland/flow_continue?direction=sold&source=hk',
      hkbuyCDays: 0,
      hksoldCDays: 0,
      dialogVisible: false,
      selectedHkCode: null,
      selectedCode: null,
      sliderPice: true,

    }
  },
  methods: {
    loadHkStatData () {
      HTTP.get('/hkmainland/fetch_northflow_stats_hk').then(dt => {
        this.hkStatsData = dt.data.list 
        this.renderHkChart() 
      })
    },
    renderHkChart () {
      let xData = this.hkStatsData.map(item => moment(item.recordDate).format('YY-MM-DD'))
      // let bsBuyCtList = this.hkStatsData.map(item => item.buyCount)
      // let bsSoldCtList = this.hkStatsData.map(item => item.soldCount)
      // let bsBuyAmtList = this.hkStatsData.map(item => item.buyAmount)
      let bsNetAmtList = this.hkStatsData.map(item => Math.abs(item.netAmount))
      const redStyle = {normal: {color: '#F37726'}}
      // const greenStyle = {normal: {color: 'green'}}
      // this.hkbs_count_chart_options = ChartHelper.buildStackedChart('买入卖出数量统计', '日期', xData, [{name: '买入公司数量', areaStyle: redStyle, data: bsBuyCtList}, {name: '卖出公司数量', areaStyle: greenStyle, data: bsSoldCtList}], this.hkcountChartType.toLocaleLowerCase())
      this.hkbs_amount_chart_options = ChartHelper.buildStackedChart('流入流出净额统计(亿元)', '日期', xData, [{name: '净额(亿)', areaStyle: redStyle, data: bsNetAmtList}], this.hkamountChartType.toLocaleLowerCase())

    },
    hkchartChange () {
      this.renderHkChart()
    },
    setHkUpdated (lastDate) {
      this.hkLastDate = lastDate
    },
    silderBuyToolip (val) {
      if(val === 0) {
        return ''
      } else {
        return `连续${val}天买入`
      }
    },
    silderSoldToolip (val) {
      if(val === 0) {
        return ''
      } else {
        return `连续${val}天卖出`
      }
    },
   
    hksliderBuyChg (val) {
      this.hkbuyCDays = val
      this.hkrefreshCBuyDataUrl()
    },
    hksliderSoldChg (val) {
      this.hksoldCDays = val
      this.hkrefhresCSoldDataUrl()
    },
    hkrefreshCBuyDataUrl () {
      if(this.hkbuyCDays > 0) {
        this.hkbuyDataUrl = `/hkmainland/flow_continue?direction=buy&source=hk&days=${this.hkbuyCDays}`

      } else {
        this.hkbuyDataUrl = '/hkmainland/flow_continue?direction=buy&source=hk'
      }
    },
    hkrefhresCSoldDataUrl () {
      if(this.hksoldCDays > 0) {
        this.hksoldDataUrl = `/hkmainland/flow_continue?direction=sold&source=hk&days=${this.hksoldCDays}`
      } else {
        this.hksoldDataUrl = '/hkmainland/flow_continue?direction=sold&source=hk'

      }
    },
    stockSelected (row) {
      console.log(row)
      this.dialogVisible = true
      this.selectedHkCode = row.hkcode
      this.selectedCode = row.stockcode
    }
  },
  mounted () {
    this.loadHkStatData()
  },
  components: {NormalFrame, IEcharts, VueTable, FlowChart, vueSlider}

}
</script>

<style lang="scss">
@import "src/styles/money-channel.scss";
</style>
