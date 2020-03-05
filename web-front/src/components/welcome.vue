<template>
  <div>
    <div class="row">
      <div class="col-md-6">
        <normal-frame title="持股量激增 TOP 12" :lastUpdate="suddenLastDate" width="100%">
          <el-tabs type="card">
            <el-tab-pane label="沪深股通">
              <vue-table :url="suddenUrl"  className="table is-striped"  @onLastUpdated="setSuddenUpdated" @onRowSelected="stockSelected"></vue-table> 
            </el-tab-pane>
            <!-- <el-tab-pane label="港股通">
              <vue-table :url="suddenHkUrl"  className="table is-striped"  @onLastUpdated="setSuddenUpdated" @onRowSelected="stockSelected"></vue-table> 
            </el-tab-pane> -->
          </el-tabs>
          <el-alert title="注意" type="warning" :closable="false">
            <label class="lbl red">选股指标：选取过去5天持有量平均值 <font style="font-weight:bold">激增</font> 超过30%，并且持有市值超过500万的标的，按持有市值倒序排列；取前12只股票形成该列表。</label>
          </el-alert>
          <div class="daterng">
            <el-radio-group v-model="incrDate" size="mini" @change="increDateChanged">
              <el-radio-button v-for="(item,i) in dateRange" v-bind:key="i" :label="item">{{item}}</el-radio-button>
            </el-radio-group>
          </div> 
        </normal-frame>
      </div>
      <div class="col-md-6">
         <normal-frame title="持股量激减 TOP 12" :lastUpdate="suddenLastDate" width="100%">
          <el-tabs type="card">
            <el-tab-pane label="沪深股通">
              <vue-table :url="suddenReduceUrl"  className="table is-striped"  @onLastUpdated="setSuddenUpdated" @onRowSelected="stockSelected"></vue-table> 
            </el-tab-pane>
            <!-- <el-tab-pane label="港股通">
              <vue-table :url="suddenHkReduceUrl"  className="table is-striped"  @onLastUpdated="setSuddenUpdated" @onRowSelected="stockSelected"></vue-table> 
            </el-tab-pane> -->
          </el-tabs>
          <el-alert title="注意" type="warning" :closable="false">
            <label class="lbl green">选股指标：选取过去5天持有量平均值 <font style="font-weight:bold">激减</font> 超过25%，并且持有市值超过200万的标的，按持有市值倒序排列；取前12只股票形成该列表。</label>
          </el-alert>
          
          <div class="daterng">
            <el-radio-group v-model="reduceDate" size="mini" @change="reduceDateChanged">
              <el-radio-button v-for="(item,i) in dateRange" v-bind:key="i" :label="item">{{item}}</el-radio-button>
            </el-radio-group>
          </div>  
        </normal-frame>
      </div>
    </div>
    <div class="row" style="margin-top:15px">
      <div class="col-md-6">
        <normal-frame title="沪深股通行业-资金增量前10"  width="100%" :lastUpdate="industryUpdateDate">
          <div class="map" v-if="industry_amount_top10_chart_options != null">
						<IEcharts :option="industry_amount_top10_chart_options" ></IECharts>
					</div>
        </normal-frame>
      </div>
      <div class="col-md-6">
        <normal-frame title="沪深股通行业-资金增量后10"  width="100%" :lastUpdate="industryUpdateDate">
          <div class="map" v-if="industry_amount_tail10_chart_options != null">
						<IEcharts :option="industry_amount_tail10_chart_options" ></IECharts>
					</div>
        </normal-frame>
      </div>
    </div>
    <div class="row" style="margin-top:15px">
      <div class="col-md-12">
        <normal-frame title="沪深股通-外资持有市值变化趋势（亿元）"  width="100%">
          <div class="map" v-if="line_industry_chart_options != null">
						<IEcharts :option="line_industry_chart_options" theme="macarons"></IECharts>
				  </div>
          <div class="insDateRangeSelector">
            <el-date-picker @change="dateRangeChanged" v-model="chartDateRange" value-format="yyyy-MM-dd" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期">
            </el-date-picker>
          </div>
        </normal-frame>
      </div>
    </div>

    <div class="row" style="margin-top:15px">
      <div class="col-md-12">
        <normal-frame title="沪深股通-外资持股量变化趋势（万股）"  width="100%">
          <div class="map" v-if="line_industry_quantity_chart_options != null">
						<IEcharts :option="line_industry_quantity_chart_options" theme="macarons"></IECharts>
				  </div>
          <div class="insDateRangeSelector">
            <el-date-picker @change="dateRangeChangedForQty" v-model="chartDateRangeQty" value-format="yyyy-MM-dd" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期">
            </el-date-picker>
          </div>
        </normal-frame>
      </div>
    </div>

    <div class="row" style="margin-top:15px">
      <div class="col-md-6">
        <normal-frame title="沪深股通行业持股-按占比统计"  width="100%">
          <div class="map" v-if="circular_bar_chart_options != null">
						<IEcharts :option="circular_bar_chart_options" ></IECharts>
					</div>
          <table class="topten">
            <tr><th>No.</th><th>行业</th><th>占比累计</th></tr>
            <tr v-for="(item, index) in circular_tb" v-bind:key="item.name">
              <td>{{index + 1}}</td><td>{{item.name}}</td><td>{{item.value}}</td>
            </tr>
          </table>
        </normal-frame>
      </div>
      <div class="col-md-6">
        <normal-frame title="沪深股通行业持股-按持有市值统计"  width="100%">
          <div class="map" v-if="holdMarket_bar_chart_options != null">
						<IEcharts :option="holdMarket_bar_chart_options" ></IECharts>
					</div>
          <table class="topten">
            <tr><th>No.</th><th>行业</th><th>持有累计</th></tr>
            <tr v-for="(item, index) in holdmarket_tb" v-bind:key="item.name">
              <td>{{index + 1}}</td><td>{{item.name}}</td><td>{{item.value}}亿</td>
            </tr>
          </table>
        </normal-frame>
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
import vueSlider from "vue-slider-component";
import NormalFrame from "@/components/common/normal-frame";
import VueTable from "@/components/common/vue-table";
import FlowChart from "@/components/common/flow-chart";
import IEcharts from "vue-echarts-v3/src/lite.vue";
import "echarts/theme/infographic";
import "echarts/theme/macarons";
import moment from "moment";
import ChartHelper from "@/core/chartHelper";
import HTTP from "@/core/fetch";
export default {
  name: "welcome",
  data() {
    return {
      suddenUrl: "/home/sudden_incres",
      suddenHkUrl: "/home/sudden_incres?source=hk",
      suddenReduceUrl: "/home/sudden_incres?stype=reduce",
      suddenHkReduceUrl: "/home/sudden_incres?stype=reduce&source=hk",
      suddenLastDate: "",
      dialogVisible: false,
      selectedHkCode: null,
      selectedCode: null,
      circular_tb: null,
      holdmarket_tb: null,
      circular_bar_chart_options: null,
      holdMarket_bar_chart_options: null,
      industry_amount_top10_chart_options: null,
      industry_amount_tail10_chart_options: null,
      line_industry_chart_options: null,
      line_industry_quantity_chart_options: null,
      industryUpdateDate: null,
      incrDate: null,
      reduceDate: null,
      dateRange: [],
      chartDateRange: ['', ''],
      chartDateRangeQty: ['', ''],
      // insStart: '',
      // insEnd: ''
    };
  },
  methods: {
    loadIndustryStatData() {
      HTTP.get(`/home/industry_stats`).then(dt => {
        this.holdmarket = dt.data.holdmarket;
        this.circular = dt.data.circular;
        this.circular_tb = this.circular.slice(0, 10);
        this.holdmarket_tb = this.holdmarket.slice(0, 10);
        this.circular_bar_chart_options = ChartHelper.buildPieChart(
          "流通占比累计",
          "流通占比累计",
          this.circular
        );
        this.holdMarket_bar_chart_options = ChartHelper.buildPieChart(
          "持有市值累计(亿元)",
          "持有市值累计",
          this.holdmarket
        );
      });
      HTTP.get(`/home/industry_amount_stats`).then(dt => {
        this.industryUpdateDate = dt.data.updateDate;
        const data = dt.data.amountStatsHead;
        const xData = data.map(item => item.name);
        const yData = data.map(item => item.value);
        this.industry_amount_top10_chart_options = ChartHelper.buildChart(
          "行业资金增量排名-前10",
          "当日资金增量(亿元)",
          xData,
          yData,
          "bar",
          "#C23736"
        );

        const data1 = dt.data.amountStatsTail;
        const xData1 = data1.map(item => item.name);
        const yData1 = data1.map(item => item.value);
        this.industry_amount_tail10_chart_options = ChartHelper.buildChart(
          "行业资金增量排名-后10",
          "当日资金增量(亿元)",
          xData1,
          yData1,
          "bar",
          "#2A933A"
        );
        
      });

      this.loadIndustryMarketValueTrend()
      this.loadIndustryQtyTrend()
    },
    loadIndustryMarketValueTrend () {
      HTTP.get(`/home/industry_incres_dates?source=hs&startDate=${this.chartDateRange[0]}&endDate=${this.chartDateRange[1]}`).then(dt => {
        this.chartDateRange = ['', '']
        this.chartDateRange[0] = dt.data.start
        this.chartDateRange[1] = dt.data.end
        if(dt.data && dt.data.stats.length > 0) {
          let list = dt.data.stats 
          let xData = dt.data.stats[0].values.map(item => moment(item.date).format('YY-MM-DD'))
          let yList = []
          list.forEach(item => {
            yList.push({name: item.name, data: item.values.map(vl => vl.value)})
          })
          this.line_industry_chart_options = ChartHelper.buildStackedChart('行业持有市值变化趋势(亿元)', '日期', xData, yList, 'line')
        } else {
          this.line_industry_chart_options = null
        }
      })
    },
    loadIndustryQtyTrend () {
      HTTP.get(`/home/industry_incres_dates?source=hs_daily_quantity&startDate=${this.chartDateRangeQty[0]}&endDate=${this.chartDateRangeQty[1]}`).then(dt => {
        this.chartDateRangeQty = ['', '']
        this.chartDateRangeQty[0] = dt.data.start
        this.chartDateRangeQty[1] = dt.data.end
        if(dt.data && dt.data.stats.length > 0) {
          let list = dt.data.stats 
          let xData = dt.data.stats[0].values.map(item => moment(item.date).format('YY-MM-DD'))
          let yList = []
          list.forEach(item => {
            yList.push({name: item.name, data: item.values.map(vl => vl.value)})
          })
          this.line_industry_quantity_chart_options = ChartHelper.buildStackedChart('行业持股量变化趋势(万股)', '日期', xData, yList, 'line')
        } else {
          this.line_industry_quantity_chart_options = null
        }
      })
    },
    loadSuddenDates() {
      HTTP.get(`/home/sudden_incres_dates`).then(dt => {
        this.incrDate = dt.data.dates[0];
        this.reduceDate = dt.data.dates[0];
        this.dateRange = dt.data.dates.reverse();
      });
    },
    setSuddenUpdated(lastDate) {
      this.suddenLastDate = lastDate;
    },
    stockSelected(row) {
      this.dialogVisible = true;
      this.selectedHkCode = row.hkcode;
      this.selectedCode = row.stockcode;
    },
    increDateChanged() {
      this.suddenUrl = `/home/sudden_incres?targetDate=${this.incrDate}`;
      this.suddenHkUrl = `/home/sudden_incres?source=hk&targetDate=${
        this.incrDate
      }`;
    },
    reduceDateChanged() {
      this.suddenReduceUrl = `/home/sudden_incres?stype=reduce&targetDate=${
        this.reduceDate
      }`;
      this.suddenHkReduceUrl = `/home/sudden_incres?stype=reduce&source=hk&targetDate=${
        this.reduceDate
      }`;
    },
    dateRangeChanged (val) {
      this.loadIndustryMarketValueTrend()
    },
    dateRangeChangedForQty (val) {
      this.loadIndustryQtyTrend()
    },
  },
  mounted() {
    this.loadSuddenDates();
    this.loadIndustryStatData();
  },
  components: { NormalFrame, IEcharts, VueTable, vueSlider, FlowChart }
};
</script>

<style lang="scss">
@import "src/styles/money-channel.scss";
.lbl {
  margin-top: 10px;
  font-weight: 300;
}
.red {
  color: brown;
}
.green {
  color: green;
}
table.topten {
  border-collapse: collapse;
  position: absolute;
  top: 45px;
  right: 5px;
}
table.topten td,
table.topten th {
  color: grey;
  border: solid 1px rgb(158, 154, 154);
  padding: 1px 8px;
  text-align: center;
}
.daterng {
  position: absolute;
  top: 5px;
  right: 10px;
}
.insDateRangeSelector {
  position: absolute;
  top: 2px;
  right: 5px;
  font-size: 12px;
  padding: 3px 0px;
}
.col-md-12 {
  padding-left: 8px;
  padding-right: 8px;
}
</style>
