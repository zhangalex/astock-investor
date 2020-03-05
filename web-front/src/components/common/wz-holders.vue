<template>
<div class="wzholders">
  <div class="row">
    <div class="col-md-12">
      <!-- <div class="tl">市场中介者/愿意披露的投资者户口持有人的纪录：</div> -->
      <div class="box">
        <vue-table :url="fetchUrl"  className="table is-striped wz" :showPager="true" @onRowSelected="holderSelected"></vue-table> 
      </div>
    </div>
  </div>
  <el-dialog
      title=""
      :visible.sync="dialogVisible"
      width="65%">
      <HolderHoldChart :code="selectedRow.code" :stockcode="selectedRow.stockcode" v-if="selectedRow != null" />
  </el-dialog>
</div>
</template>

<script>
import HTTP from "@/core/fetch"
import ChartHelper from '@/core/chartHelper'
import HolderHoldChart   from '@/components/common/holderhold-chart'
import VueTable    from '@/components/common/vue-table'
export default {
  name: 'wzHolders',
  props: {
    stockcode: {
      type: String,
      required: true,
      default: null
    },
    recordDate: {
      type: String,
      required: false,
      default: ''
    },
    perPage: {
      type: Number,
      required: false,
      // default: 0
    },
    isLongColumn: {
      type: Number,
      required: false,
      // default: 0 
    }
  },
  data () {
    return {
      fetchUrl: `/hkmainland/wz_holders?stockcode=${this.stockcode}&recordDate=${this.recordDate}&perPage=${this.perPage ? this.perPage : ''}&isLongColumn=${this.isLongColumn ? this.isLongColumn : ''}`,
      dialogVisible: false,
      selectedRow: null
    }
  },
  methods: {
    holderSelected (row) {
      this.selectedRow = row
      this.dialogVisible = true
    }
  },
  mounted () {
  },
  watch : {
    stockcode () {
      this.fetchUrl = `/hkmainland/wz_holders?stockcode=${this.stockcode}&recordDate=${this.recordDate}&perPage=${this.perPage ? this.perPage : ''}&isLongColumn=${this.isLongColumn ? this.isLongColumn : ''}`
    }
  },
  components: { VueTable, HolderHoldChart}
  
}
</script>
<style lang='scss'>
.el-dialog__body {
  padding: 0px 20px;
}
table.wz {
  font-size: 13px;
}
table.wz tr.selected{
  background-color: rgb(143, 221, 245);
}
</style>
<style lang='scss' scoped>
.wzholders {
}
.tl {
  text-align: left;
  padding: 5px 0px;
}
</style>
