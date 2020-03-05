<template>
  <div>
    <div class="row">
      <div class="col-md-6 splitter">
        <normal-frame title="沪股通-深股通-港通持股纪录" :lastUpdate="hsLastDate" width="100%">
          <div class="gtSelector">
            <el-radio-group v-model="sourceValue"  size="mini" @change="changeSource">
              <el-radio-button label="">全部(除港股通)</el-radio-button>
              <el-radio-button label="sh">沪股通(北上)</el-radio-button>
              <el-radio-button label="sz">深股通(北上)</el-radio-button>
              <!-- <el-radio-button label="hk">港股通(南下)</el-radio-button> -->
              <el-radio-button label="msci">MSCI A股</el-radio-button>
              <el-radio-button label="myliked">我的自选</el-radio-button>
            </el-radio-group>
          </div>
          <vue-table :url="dataUrl"  className="table is-striped" :showPager="true" @onRowSelected="stockSelected" @onDataChange="tableDataChange" @onLastUpdated="setHsUpdated" @onDataLoadCompeleted="dataCompleted"></vue-table> 
          <div class="opt">
            <input type="text" class="search" placeholder="请输入名称或代码来搜索(清空并按回车可取消搜索)" v-model="searchValue" v-on:keyup.13="search" />
          </div>
          <el-alert title="注意" type="warning" :closable="false">
            <div class="tip"><i class="fa fa-hand-o-right" aria-hidden="true"></i> "M" 标记: 表示已经纳入MSCI中国A股指数成份股; 数据搜索前置条件是您选中的tab项。</div>
          </el-alert>
        </normal-frame>
        <div class="news">
          <el-tabs type="border-card">
            <el-tab-pane label="市场参与者详情(特指愿意披露投资者)">
              <Wzholders :stockcode="currentRow.stockcode" :recordDate="currentRow.recordDate" v-if="currentRow != null" />
            </el-tab-pane>
            <el-tab-pane label="公告">
              <div v-if="showLoad"><img src="~assets/images/loading.gif" style="width: 40px;height: 40px;"/></div>
              <!-- <a @click="loadNotice" class="loadBtn" v-if="!isEmptyChart">加载</a> -->
              <table v-if="noticeList.length > 0" class="strip">
                <tr><th>标题</th><th>日期</th><th>类别</th></tr>
                <tr v-for="item in noticeList" v-bind:key="item.id">
                  <td width="65%"><a v-bind:href="item.url" target="_blank">{{item.title}}</a></td><td width="15%" :class="{marked: item.isMarked}">{{item.time}}</td><td width="20%" :class="{marked: item.isMarked}">{{item.type}}</td>
                </tr>
              </table>
            </el-tab-pane>
            <!-- <el-tab-pane label="财报"></el-tab-pane> -->
            <el-tab-pane label="定期报告">
              <RegularReport :code="currentCode"></RegularReport>
            </el-tab-pane>
              
            <!-- <el-tab-pane label="股东">
              <label v-if='gdReportDate != null' style="font-weight:300;color:#000">
                <i class="fa fa-lightbulb-o" aria-hidden="true"></i>
                最近更新日期：{{gdReportDate}} ，点击股东名称，查看其它持仓
              </label>
              <table v-if="ltgdList.length > 0" class="strip">
                <tr><td colspan="5" style="border-bottom: dashed 1px grey">十大流通股东</td></tr>
                <tr><th>股东名称</th><th style="text-align:center;">股东类型</th><th>持股数(股)</th><th>占股比例</th><th style="text-align:center;">变化</th></tr>
                <tr v-for="item in ltgdList" v-bind:key="item.holderName" :class="{'red': item.change == '新进', 'brown': item.change == '增加', 'green': item.change =='减少'}">
                  <td><a @click="showRelation(item)">{{item.holderName}}</a></td><td style="text-align:center;">{{item.holderType}}</td><td>{{item.holdQuantity}}</td><td width="5%">{{item.stockPercent}}%</td><td style="text-align:center;">{{item.change}}</td>
                </tr>
              </table>
              <table v-if="gdList.length > 0" class="strip" style="margin-top: 10px">
                <tr><td colspan="5" style="border-bottom: dashed 1px grey">十大股东</td></tr>
                <tr><th>股东名称</th><th style="text-align:center;">股东类型</th><th>持股数(股)</th><th>占股比例</th><th style="text-align:center;">变化</th></tr>
                <tr v-for="item in gdList" v-bind:key="item.holderName" :class="{'red': item.change == '新进', 'brown': item.change == '增加', 'green': item.change =='减少'}">
                  <td><a @click="showRelation(item)">{{item.holderName}}</a></td><td style="text-align:center;">{{item.holderType}}</td><td>{{item.holdQuantity}}</td><td width="5%">{{item.stockPercent}}%</td><td style="text-align:center;">{{item.change}}</td>
                </tr>
              </table>
            </el-tab-pane> -->
           
          </el-tabs>
        </div>
      </div>
      <div class="col-md-6">
        <div class="chart">
          <h3 v-if="isEmptyChart">选择表格中的数据行，显示图表</h3>
          <div class="box" v-if="!isEmptyChart">
            <IEcharts :option="line_option" :loading="loading" @ready="onReady"></IEcharts>
          </div>
          <div class="dateRangeSelector" v-if="!isEmptyChart"><el-date-picker @change="dateRangeChanged" v-model="chartDateRange" value-format="yyyy-MM-dd" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"></el-date-picker></div>
        </div>        
        <div class="details">
          <vue-table :url="detailUrl"  className="table is-striped" :showPager="false" v-if="currentRow != null"></vue-table> 
        </div>
        <!-- <div class="details">
          <XueqiuData :stockcode="selectedCode" v-if="selectedCode"></XueqiuData>
        </div> -->
        <!-- <div class="ref">
          <h5>沪港通及深港通持股纪录</h5>
          <a href="http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/mutualmarketsdw/main_c.htm">主站</a>
          <a href = "http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh" target="_blank">沪股通</a>  
          <a href = "http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sz" target="_blank">深股通</a>  
          <a href = "http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=hk" target="_blank">港股通(沪) 及 港股通(深)</a>  
          <h5>东方财富网</h5>
          <a href = "http://data.eastmoney.com/zjlx/detail.html" target="_blank">个股资金流向</a>
        </div>  -->
      </div>
    </div>
    <el-dialog
      title=""
      :visible.sync="holderDialogVisible"
      width="40%">
      <Shareholders :holderName="currentHolderName" :holderCategory="currentHolderCategory"></Shareholders>
    </el-dialog>
  </div>
</template>

<script>
import NormalFrame from '@/components/common/normal-frame'
import VueTable    from '@/components/common/vue-table'
import RegularReport    from '@/components/common/regular-report'
import Shareholders    from '@/components/common/shareholders'
import Wzholders    from '@/components/common/wz-holders'
import XueqiuData    from '@/components/common/xueqiu-data'
import IEcharts    from 'vue-echarts-v3/src/lite.vue'
import 'echarts/lib/component/title'
import 'echarts/lib/chart/line'
import 'echarts/lib/chart/bar'
import 'echarts/lib/component/legend'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/toolbox'
// import 'echarts/theme/infographic'
import $ from 'jQuery'
import moment from 'moment'
import ChartHelper from '@/core/chartHelper'
import HTTP from "@/core/fetch"
export default {
  name: 'hk-mainland',
  data () {
    return {
      hsLastDate: null,
      loading: false,
      line_option: {},
      eChartsIns: null,
      isEmptyChart: true,
      attenChecked: false,
      dataUrl: '/hkmainland/north_flows',
      detailUrl: '',
      searchValue: '',
      sourceValue: '',
      chartDateRange: ['', ''],
      currentRow: null,
      currentCode: "",
      selectedCode: "",
      noticeList: [],
      ltgdList: [],
      gdList: [],
      gdReportDate: null,
      showLoad: false,
      holderDialogVisible: false,
      currentHolderName: null,
      currentHolderCategory: 0,
      gtselected: 'all'
      // loadingImg: require('@/static/loading.gif')
    }
  },
  methods: {
    stockSelected (row) {
      
      const url = '/hkmainland/north_chart?hkcode=' + row.hkcode
      this.currentRow = row
      if(row.source !== 'hk') {
        this.currentCode = row.stockcode
      } else {
        this.currentCode = ""
      }
      this.selectedCode = row.stockcode 

      HTTP.get(url).then((dt) => {
        // console.log(dt.data)
        this.isEmptyChart = false
        this.line_option = ChartHelper.buildFlowChart(dt.data)
        this.chartDateRange = ['', '']
        this.chartDateRange[0] = dt.data.start
        this.chartDateRange[1] = dt.data.end
        this.detailUrl = `/hkmainland/flow_detail?hkcode=${row.hkcode}`
      })
      this.detailUrl = `/hkmainland/flow_detail?hkcode=${row.hkcode}`
      this.noticeList = []
      this.ltgdList = []
      this.gdList = []
      this.gdReportDate = null

      this.showLoad = true
      setTimeout(()=> {
        this.loadHolders()
        this.loadNotice()
      }, 2000)
      
      

    },
    onReady (ins) {
      this.eChartsIns = ins
    },
    setHsUpdated (lastDate) {
      this.hsLastDate = lastDate 
    },
    tableDataChange () {
      if(this.eChartsIns != null) {
        // console.log(this.eChartsIns)
        // this.eChartsIns.clear()
        this.isEmptyChart = true
      }
      this.detailUrl = ''
      this.noticeList = []
      this.ltgdList = []
      this.gdList = []
      this.gdReportDate = null
      this.currentRow = null
      this.selectedCode = null
    },
    search () {
      this.refreshDataUrl()
    },
    changeSource () {
      if(this.sourceValue === 'myliked') {
        this.attenChecked = true
      } else {
        this.attenChecked = false
      }
      this.refreshDataUrl()
    },
    refreshDataUrl () {
      // const source = this.sourceValue === 'myliked' ? '' : this.sourceValue
      let source = this.sourceValue
      if(this.attenChecked) {
        this.dataUrl = `/hkmainland/north_flows?attention=true&searchValue=${this.searchValue}&source=${source}`
      } else {
        if (source === 'msci') {
          this.dataUrl = `/hkmainland/north_flows?searchValue=${this.searchValue}&msci=true&&source=`
        } else {
          this.dataUrl = `/hkmainland/north_flows?searchValue=${this.searchValue}&source=${source}`
        }
      }
    },
    dataCompleted (data) {
      setTimeout(() => {
        $('td.custom').find('span.flag').remove()
        $('td.custom').each((i, item) => {
          // console.log($(item).text())
          let cellName = $.trim($(item).text())
          let existedItem = data.list.find(item => item.stockname === cellName)
          if(existedItem && existedItem.isMsci) {
            // console.log(existedItem)
            $('<span />').addClass('flag').text('M').appendTo($(item))
          }
        })

      }, 200)
      
    },
    dateRangeChanged () {
      console.log(this.chartDateRange)
      if(this.chartDateRange != null && this.currentRow != null && this.chartDateRange[0] && this.chartDateRange[1]) {
        let [start, end] = this.chartDateRange
        const url = `/hkmainland/north_chart?hkcode=${this.currentRow.hkcode}&start=${start}&end=${end}` 
        HTTP.get(url).then((dt) => {
          this.line_option = ChartHelper.buildFlowChart(dt.data)
          this.isEmptyChart = false
        })

      }
    },
    loadNotice () {
      const HEAD_URL = 'http://www.cninfo.com.cn/'
      if(this.currentRow != null && this.currentRow.stockcode && this.currentRow.source !== 'hk') {
        this.showLoad = true
        HTTP.get(`/hkmainland/fetch_stock_notice?code=${this.currentRow.stockcode}`).then(dt => {
          // console.log(dt.data)
          if(dt.data) {
            let list = dt.data.classifiedAnnouncements
            let items = []
            list.forEach(notice => {
              items.push(...notice)
            })
            
            this.noticeList = items.map(item => {
              let atime = moment.unix(parseInt(item.announcementTime) / 1000).format("YYYY-MM-DD")
              let isMarked = false 
              // console.log(moment(atime, "YYYY-MM-DD"), moment().day(-1))
              if(moment(atime, "YYYY-MM-DD") >= moment().day(-1)) {
                isMarked = true
              }
              return {url: `${HEAD_URL}${item.adjunctUrl}`, time: atime, title: item.announcementTitle, type: item.announcementTypeName, id: item.announcementId, isMarked: isMarked}
            })
            // console.log(this.noticeList)
          }
          this.showLoad = false
        })
      } else {
        this.noticeList = []
        this.showLoad = false
      }
      
    },
    loadHolders () {
      // if(this.currentRow != null && this.currentRow.stockcode && this.currentRow.source !== 'hk') {
      //   HTTP.get(`/hkmainland/fetch_shareholders?code=${this.currentRow.stockcode}`).then(dt => {
      //     const data = dt.data 
      //     this.ltgdList = data.ltgdList
      //     this.gdList = data.gdList
      //     this.gdReportDate = data.reportDate
      //   })
      // } else {
      //   this.ltgdList = []
      //   this.gdList = []
      //   this.gdReportDate = null
      // }
    },
    showRelation (item) {
      console.log(item)
      this.currentHolderName = item.holderName 
      this.currentHolderCategory = item.category 
      this.holderDialogVisible = true
    },
    
  },
  mounted () {
  },
  components: { NormalFrame, VueTable, IEcharts, Shareholders, RegularReport, Wzholders, XueqiuData }

}
</script>
<style lang="scss">
a {
  cursor: pointer;
}
.el-date-editor .el-range-separator {
  width: 7%;
}
.normal_frame .table td.custom {
  position: relative;
}
.normal_frame .table td.custom > span{
  position: absolute;
  top: 2px;
  right: 0px;
  font-size: 8px;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: yellow;
  // border: solid 1px #BFBFBF;
}
.el-date-editor .el-range-input, .el-date-editor .el-range-separator {
  font-size: 12px;
}
.el-tabs--border-card>.el-tabs__content {
  padding: 10px;
}
.el-tabs {
  min-height: 300px;
}
</style>
<style lang="scss" scoped>
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
.col-md-6 {
  margin-bottom: 10px;
  padding-right: 1px;
}
.details {
  background-color: #F8F8F8;
  min-height: 200px;
  margin: 10px 0px;
  border: solid 1px #EDF0F5;
  padding: 5px;
  table {
    font-size: 13px;
  }
}
.opt {
  position: absolute;
  top: 3px;
  right: 95px;
  font-size: 13px;
  padding: 5px 0px;
}
.opt > input[type='text'] {
  -webkit-appearance: none;
  background-color: #fff;
  background-image: none;
  margin-right: 10px;
  border: solid 1px silver;
  box-sizing: border-box;
  padding: 2px 2px;
  transition: border-color .2s cubic-bezier(.645,.045,.355,1);
  border-radius: 2px;
  width: 305px;
}
.opt > input[type='text']:focus {
  outline: none;
  border-color: black;
}
.opt > select { 
  margin-right: 10px;
  border: solid 1px silver;
  box-sizing: border-box;
  padding: 1px 2px;
  transition: border-color .2s cubic-bezier(.645,.045,.355,1);
  border-radius: 2px;
}
.news {
  text-align: left;
  background-color: #F8F8F8;
  min-height: 200px;
  margin: 10px 0px;
  // border: solid 1px silver;
  // padding: 5px 10px;
  padding: 0px;
  position: relative;
}
.news h5{
  font-weight: 400;
}
.news table {
  width: 100%;
}
.news table td {
  padding: 5px 0px;
  font-size: 13px;
}
.news .loadBtn {
  position: absolute;
  right: 15px;
  top: 10px;
  cursor: pointer;
}
.news a {
  color: #3683B6;
}
.news a:hover {
  color: red;
}
.news td.marked {
  color: red;
}
.ref {
  text-align: left;
  margin-top: 10px;
  border: solid 1px silver;
  border-radius: 5px;
  padding: 10px;
}
.ref h5{
  font-weight: 400;

}
.ref a{
  margin-right: 15px;
  color: grey;
  text-decoration: underline;
}
.ref a:hover{
  color: red;
}
.ref a:active{
  color: red;
}
.input-with-select {
  margin: 2px 0px 10px 0px;
}
.red {
  color: red;
}
.green {
  color: green;
}
.brown {
  color: #D25352;
}
.tip {
  text-align: left;
  font-size: 12px;
  color: #676767;
}
.dateRangeSelector {
  text-align: center;
}
.gtSelector {
  text-align: center;
}
</style>

