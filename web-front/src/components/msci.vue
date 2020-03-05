<template>
  <div>
    <div class="row">
      <div class="col-md-5">
        <normal-frame title="MSCI A股成份股"  width="100%">
          <vue-table url="/msci/list"  className="table is-striped" :showPager="true"></vue-table> 
        </normal-frame>
      </div>
      <div class="col-md-7">
        <div class="map" v-if="pie_option != null">
          <IEcharts :option="pie_option"></IEcharts>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NormalFrame from '@/components/common/normal-frame'
import VueTable    from '@/components/common/vue-table'
import IEcharts    from 'vue-echarts-v3/src/lite.vue'
import ChartHelper from '@/core/chartHelper'
import 'echarts/lib/component/title'
import 'echarts/lib/chart/pie'
import 'echarts/lib/component/legend'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/toolbox'
import HTTP from "@/core/fetch"

export default {
  name: 'msci',
  data () {
    return {
      pie_option: null
    }
  },
  methods: {
    loadChartData () {
      HTTP.get('/msci/chart').then((dt) => {
        this.pie_option = ChartHelper.buildPieChart('MSCI A股 占比最高前20 行业分布', '占比', dt.data.list)
        this.pie_option.title.textStyle = {
          color: 'grey',
          fontFamily: 'Helvetica',
          fontSize: 14
        }

      })
      
    }
  },
  mounted () {
    this.loadChartData()
  },
  components: { NormalFrame, VueTable, IEcharts }

}
</script>

<style lang="scss" scoped>
.map {
  height: 520px;
}
</style>


