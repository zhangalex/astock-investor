<template>
  <div>
    <div class="row">
      <!-- <div class="col-md-6">
        <normal-frame title="沪深股通-买入卖出-数量统计"  width="100%">
          	<div class="map" v-if="bs_count_chart_options != null">
							<IEcharts :option="bs_count_chart_options" theme="macarons"></IECharts>
						</div>
        </normal-frame>
        <div class="chartTypeSelector">
          <el-radio-group v-model="countChartType"  size="mini" @change="chartChange">
          <el-radio-button label="Line"></el-radio-button>
          <el-radio-button label="Bar"></el-radio-button>
          </el-radio-group>
        </div>
      </div> -->
      <div class="col-md-12">
        <normal-frame title="沪深股通-流入流出-净额统计"  width="100%">
          	<div class="map" v-if="bs_amount_chart_options != null">
							<IEcharts :option="bs_amount_chart_options" theme="infographic"></IECharts>
						</div>
        </normal-frame>
        <div class="chartTypeSelector">
          <el-radio-group v-model="amountChartType"  size="mini" @change="chartChange">
          <el-radio-button label="Line"></el-radio-button>
          <el-radio-button label="Bar"></el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </div>
    <div class="row" style="margin-top:15px">
      <div class="col-md-6">
        <normal-frame title="沪深股通-连续买入" :lastUpdate="hsLastDate" width="100%">
          <vue-table :url="buyDataUrl"  className="table is-striped" :showPager="true" @onLastUpdated="setHsUpdated" @onRowSelected="stockSelected"></vue-table> 
        </normal-frame>
        <div class="block">
          <vueSlider v-model="buyCDays" :min="0" :max="30" :interval="1"  :piecewise="true" tooltip="hover"  @callback="sliderBuyChg"></vueSlider>
        </div>
      </div>
      <div class="col-md-6">
        <normal-frame title="沪深股通-连续卖出" :lastUpdate="hsLastDate" width="100%">
          <vue-table :url="soldDataUrl"  className="table is-striped" :showPager="true" @onLastUpdated="setHsUpdated" @onRowSelected="stockSelected"></vue-table> 
        </normal-frame>
        <div class="block">
          <vueSlider v-model="soldCDays" :min="0" :max="30" :interval="1"  :piecewise="true" tooltip="hover"  @callback="sliderSoldChg"></vueSlider>
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
  name: 'HsgtBuyAndSold',
  data () {
    return {
      bs_count_chart_options: null,
      bs_amount_chart_options: null,
      countChartType: 'Line',
      amountChartType: 'Line',
      statsData: null,
      hsLastDate: null,
      buyDataUrl: '/hkmainland/flow_continue?direction=buy',
      soldDataUrl: '/hkmainland/flow_continue?direction=sold',
      buyCDays: 0,
      soldCDays: 0,
      dialogVisible: false,
      selectedHkCode: null,
      selectedCode: null,
      sliderPice: true,
    }
  },
  methods: {
    loadStatData () {
      HTTP.get('/hkmainland/fetch_northflow_stats_hs').then(dt => {
        this.statsData = dt.data.list 
        this.renderChart() 
      })
    },
    
    renderChart () {
      let xData = this.statsData.map(item => moment(item.recordDate).format('YY-MM-DD'))
      // let bsBuyCtList = this.statsData.map(item => item.buyCount)
      // let bsSoldCtList = this.statsData.map(item => item.soldCount)
      let bsNetAmtList = this.statsData.map(item => item.netAmount)
      // let bsSoldAmtList = this.statsData.map(item => Math.abs(item.soldAmount))
      const redStyle = {normal: {color: '#F37726'}}
      const greenStyle = {normal: {color: 'green'}}
      // this.bs_count_chart_options = ChartHelper.buildStackedChart('买入卖出数量统计', '日期', xData, [{name: '买入公司数量', areaStyle: redStyle, data: bsBuyCtList}, {name: '卖出公司数量', areaStyle: greenStyle, data: bsSoldCtList}], this.countChartType.toLocaleLowerCase())
      // this.bs_amount_chart_options = ChartHelper.buildStackedChart('流入流出金额统计(亿元)', '日期', xData, [{name: '买入金额(亿)', areaStyle: redStyle, data: bsBuyAmtList}, {name: '卖出金额(亿)', areaStyle: greenStyle, data: bsSoldAmtList}], this.amountChartType.toLocaleLowerCase())
      this.bs_amount_chart_options = ChartHelper.buildStackedChart('流入流出净额统计(亿元)', '日期', xData, [{name: '净额(亿)', areaStyle: redStyle, data: bsNetAmtList}], this.amountChartType.toLocaleLowerCase())

    },
    
    chartChange () {
      this.renderChart()
    },
    
    setHsUpdated (lastDate) {
      this.hsLastDate = lastDate 
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
    sliderBuyChg (val) {
      this.buyCDays = val
      this.refreshCBuyDataUrl()
    },
    sliderSoldChg (val) {
      this.soldCDays = val
      this.refhresCSoldDataUrl()
    },
    refreshCBuyDataUrl () {
      if(this.buyCDays > 0) {
        this.buyDataUrl = `/hkmainland/flow_continue?direction=buy&days=${this.buyCDays}`

      } else {
        this.buyDataUrl = '/hkmainland/flow_continue?direction=buy'
      }
    },
    refhresCSoldDataUrl () {
      if(this.soldCDays > 0) {
        this.soldDataUrl = `/hkmainland/flow_continue?direction=sold&days=${this.soldCDays}`
      } else {
        this.soldDataUrl = '/hkmainland/flow_continue?direction=sold'

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
    this.loadStatData()
  },
  components: {NormalFrame, IEcharts, VueTable, FlowChart, vueSlider}

}
</script>

<style lang="scss">
@import "src/styles/money-channel.scss";

</style>
