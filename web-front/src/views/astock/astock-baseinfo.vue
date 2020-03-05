<template>
  <div>
    <div class="row">
      <div class="col-md-6">
        <normal-frame title="A股上市公司地理分布"  width="100%">
          	<div class="map" v-if="map_chart_options != null">
							<IEcharts :option="map_chart_options" theme="infographic"></IECharts>
						</div>
        </normal-frame>
      </div>
      <div class="col-md-6">
        <normal-frame title="A股上市公司区域统计"  width="100%">
          	<div class="map" v-if="bar_chart_options != null">
							<IEcharts :option="bar_chart_options" theme="infographic"></IECharts>
						</div>
        </normal-frame>
      </div>
    </div>
    <div class="row" style="margin-top:15px;">
      <div class="col-md-6">
        <normal-frame title="A股上市公司基本状况"  width="100%">
          <vue-table :url="baseInfoUrl"  className="table is-striped" :showPager="true" @onRowSelected="stockSelected"></vue-table> 
        </normal-frame>
      </div>
      <div class="col-md-6">
        <normal-frame title="MSCI A股成分股 基本状况"  width="100%">
          <vue-table :url="msciInfoUrl"  className="table is-striped" :showPager="true" @onRowSelected="stockSelected"></vue-table> 
        </normal-frame>
      </div>
    </div>
    <div class="row" style="margin-top:15px;">
      <div class="col-md-6">
        <normal-frame title="A股历史IPO按年统计"  width="100%">
          	<div class="map" v-if="line_ipo_year_chart_options != null">
							<IEcharts :option="line_ipo_year_chart_options" theme="macarons"></IECharts>
						</div>
        </normal-frame>
      </div>
      <div class="col-md-6">
        <normal-frame title="A股历史IPO按月统计"  width="100%">
          	<div class="map" v-if="line_ipo_yearMonth_chart_options != null">
							<IEcharts :option="line_ipo_yearMonth_chart_options" theme="macarons"></IECharts>
						</div>
        </normal-frame>
      </div>
    </div>
    <el-dialog
      title=""
      :visible.sync="dialogVisible"
      width="85%">
      <iframe id="xueqiu" :src="astockUrl" style="border: 0" margin="0" padding="0" frameborder="0" scrolling="yes" width="100%" height="600px" />
    </el-dialog>
  </div>
</template>

<script>
import NormalFrame from '@/components/common/normal-frame'
import IEcharts from 'vue-echarts-v3/src/lite.vue'
import VueTable    from '@/components/common/vue-table'
import china from 'echarts/map/js/china'
import 'echarts/theme/infographic'
import 'echarts/theme/macarons'
import ChartHelper from '@/core/chartHelper'
import HTTP from "@/core/fetch"
import $ from 'jQuery'
export default {
  name: 'astockBaseInfo',
  data () {
    return {
      map_chart_options: null,
      bar_chart_options: null,
      dialogVisible: false,
      baseInfoUrl: '/astock/baseinfo',
      msciInfoUrl: '/astock/baseinfo?qtype=msci',
      astockUrl: '',
      line_ipo_year_chart_options: null, 
      line_ipo_yearMonth_chart_options: null

    }
  },
  methods: {
    loadMapChartData () {
      HTTP.get('/astock/statistic').then(dt => {
        // console.log(dt.data.list)
        const geoLabels = ['上市公司地理位置']
        this.map_chart_options = ChartHelper.buildGeomapChart('上市公司地理分布', '数量', dt.data.list, geoLabels)
        const sortedData = dt.data.list.sort((a, b) => b.value - a.value)
        const xData = sortedData.map(item => item.name)
        const yData = sortedData.map(item => item.value)
        // console.log(sortedData)
        this.bar_chart_options = ChartHelper.buildChart('上市公司区域统计', '数量', xData, yData, 'bar')

      })
      HTTP.get(`/astock/ipo_statistic`).then(dt => {
        const sortedData = dt.data.list
        const xData = sortedData.map(item => item.name)
        const yData = sortedData.map(item => item.value)
        this.line_ipo_year_chart_options = ChartHelper.buildChart('A股IPO统计（按年）', '数量', xData, yData, 'line')

      })
      HTTP.get(`/astock/ipo_statistic?statBy=month`).then(dt => {
        const sortedData = dt.data.list
        const xData = sortedData.map(item => item.name)
        const yData = sortedData.map(item => item.value)
        this.line_ipo_yearMonth_chart_options = ChartHelper.buildChart('A股IPO统计（按月）', '数量', xData, yData, 'line')

      })
    },
    stockSelected (row) {
      // console.log(row)
      this.dialogVisible = true
      // this.selectedCode = row.code
      const firstChar = row.code[0]
      const code = (firstChar === '5' || firstChar === '6' || firstChar === '9') ? `SH${row.code}` : `SZ${row.code}`
      this.astockUrl = `https://xueqiu.com/S/${code}`

      // setTimeout(() => {
      //   $("iframe").contents().find('.enter-fs').children('a').click()
      // }, 2000)
    }
  },
  mounted () {
    this.loadMapChartData()
  },
  components: {NormalFrame, IEcharts, VueTable}

}
</script>

<style lang="scss">
#xueqiu .stickyFixed {
  display: none;
}
.el-dialog__wrapper {
  top: -40px;
}
.el-dialog__body {
  padding-top: 10px;
}
.map {
	height: 420px;
	padding: 10px 0px;
}
</style>
