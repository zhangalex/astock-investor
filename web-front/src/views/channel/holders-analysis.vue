<template>
  <div class="holders-analysis">
    <div class="row">
      <div class="col-md-4">
        <el-input placeholder="请输入机构名称" v-model="holderName" @keyup.enter.native="searchByName">
          <template slot="prepend">名称：</template>
          <el-button slot="append" icon="el-icon-search"></el-button>
        </el-input>

        <!-- <common-search url="/holders/hsgt" :searchCallback="searchCallabck" placeHolder="请输入机构名称或者拼音"></common-search> -->
      </div>
    </div>
    <div class="row">
      <div class="candidate">
        <ul>
        <li v-for="(item,index) in candidateList" v-bind:key="index"><a @click.stop="searchCallabck(item)">[{{item.code}}]{{item.name}} ({{item.marketValue}})</a></li>
        </ul>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6">
        <normal-frame :title="tbTitle" :lastUpdate="lastDate" width="100%" v-if="fetchStocksUrl !== ''">
          <vue-table :url="fetchStocksUrl"  className="table is-striped" :showPager="true" @onLastUpdated="setUpdated" @onRowSelected="stockSelected"></vue-table> 
        </normal-frame>
        <div class="sourceSelector" v-if="fetchStocksUrl !== ''">
          <el-radio-group v-model="stockSource"  size="mini" @change="sourceChange">
          <el-radio-button label="hs">A股</el-radio-button>
          <!-- <el-radio-button label="hk">港股</el-radio-button> -->
          </el-radio-group>
        </div>
      </div>
      <div class="col-md-6">
        <div class="chart" v-if="fetchStocksUrl !== ''">
          <HolderHoldChart :code="selectedRow.code" :stockcode="selectedRow.stockcode" v-if="selectedRow != null"  />
        </div>
        <!-- <div class="chart" style="margin-top:15px;" v-if="fetchStocksUrl !== ''">
          <h3 v-if="isEmptyChart">选择表格中的数据行，显示图表</h3>
          <div class="box" v-if="!isEmptyChart">
            <IEcharts :option="line_option" :loading="loading" @ready="onReady"></IEcharts>
          </div>
          <div class="dateRangeSelector" v-if="!isEmptyChart"><el-date-picker @change="dateRangeChanged" v-model="chartDateRange" value-format="yyyy-MM-dd" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"></el-date-picker></div>
        </div>        -->

      </div>
    </div>
  </div>
</template>

<script>
import CommonSearch    from '@/components/common/common-search'
import NormalFrame from '@/components/common/normal-frame'
import VueTable    from '@/components/common/vue-table'
import HolderHoldChart   from '@/components/common/holderhold-chart'
import IEcharts    from 'vue-echarts-v3/src/lite.vue'
import 'echarts/lib/component/title'
import 'echarts/lib/chart/line'
import 'echarts/lib/chart/bar'
import 'echarts/lib/component/legend'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/toolbox'
import ChartHelper from '@/core/chartHelper'
import HTTP from "@/core/fetch"
export default {
  name: 'holders-analysis',
  data () {
    return {
      lastDate: null,
      fetchStocksUrl: '',
      tbTitle: '机构持有股票',
      isEmptyChart: true,
      line_option: {},
      loading: false,
      chartDateRange: ['',''],
      currentItem: null,
      selectedRow: null,
      stockSource: null,
      holderName: '',
      candidateList: []
    }
  },
  mounted () {
    console.log(this.$route.params)
    if(this.$route.params && this.$route.params.name) {
      this.holderName = this.$route.params.name
      this.searchCallabck(this.$route.params)
    }
  },
  methods: {
    searchCallabck (item) {
      console.log(item)
      this.stockSource = 'hk'
      this.currentItem = item
      this.tbTitle = `${item.name} 持有股票列表`
      this.fetchStocksUrl = `/hkmainland/holders_analysis?code=${item.code}&source=${this.stockSource}`
    },
    setUpdated (date) {
      this.lastDate = date
    },
    stockSelected (row) {
      this.selectedRow = row 

      // const url = '/hkmainland/north_chart?hkcode=' + row.hkcode
      // this.currentRow = row
      // if(row.source !== 'hk') {
      //   this.currentCode = row.stockcode
      // } else {
      //   this.currentCode = ""
      // }
      // HTTP.get(url).then((dt) => {
      //   this.isEmptyChart = false
      //   this.line_option = ChartHelper.buildFlowChart(dt.data)
      //   this.chartDateRange = ['', '']
      //   this.chartDateRange[0] = dt.data.start
      //   this.chartDateRange[1] = dt.data.end
      // })

    },
    // dateRangeChanged () {
    //   console.log(this.chartDateRange)
    //   if(this.chartDateRange != null && this.currentRow != null && this.chartDateRange[0] && this.chartDateRange[1]) {
    //     let [start, end] = this.chartDateRange
    //     const url = `/hkmainland/north_chart?hkcode=${this.currentRow.hkcode}&start=${start}&end=${end}` 
    //     HTTP.get(url).then((dt) => {
    //       this.line_option = ChartHelper.buildFlowChart(dt.data)
    //       this.isEmptyChart = false
    //     })

    //   }
    // },
    onReady (charts) {

    },
    sourceChange () {
      this.fetchStocksUrl = `/hkmainland/holders_analysis?code=${this.currentItem.code}&source=${this.stockSource}`
    },
    searchByName () {
      if(this.holderName.length > 1) {
        HTTP.get(`/hkmainland/holders_query?name=${this.holderName}`).then(dt => {
          console.log(dt.data.list)
          this.candidateList = dt.data.list
          this.fetchStocksUrl = ''
        })
      } else {
        this.candidateList = []
        this.$message({message: '请输入名称，且名称长度必须大于一个字符。', type: 'error'})
      }

    }
  },
  components: { CommonSearch, NormalFrame, VueTable, IEcharts, HolderHoldChart}
}
</script>

<style lang='scss' scoped>
.chart {
  background-color: #F8F8F8;
  min-height: 300px;
  margin: 0px;
  border: solid 1px #EDF0F5;
  padding: 5px;
}
.chart h3{
  text-align: center;
  color: grey;
  margin-top: 30px;
  font-size: 18px;
}
.chart .box {
  height: 380px;
}
.dateRangeSelector {
  text-align: center;
}
.col-md-6 {
  position: relative;
}
.sourceSelector {
  position: absolute;
  right: 22px;
  top: 6px;
}
.candidate {
  padding: 10px 15px;
  ul {
    padding: 0px;
    margin: 0px 0px 0px 15px;
    li {
      list-style-type: decimal;
      padding: 2px;
    }
  }
  a {
    color: grey;
    &:hover {
      color: red;
    }
  }
}
</style>
