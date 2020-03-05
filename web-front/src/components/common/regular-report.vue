<template>
<div class="regular_report">
  <table>
    <tr v-for="item in reports" v-bind:key="item.title">
      <td><a :href="item.url" target="_blank">{{item.title}}</a></td><td>{{item.date}}</td>
    </tr>
  </table>

</div>
</template>

<script>
import HTTP from "@/core/fetch"
import moment from 'moment'
export default {
  name: 'regular-report',
  props: {
    code: {
      type: String,
      required: true,
      default: null
    }
  },
  data () {
    return {
      reports: []
    }
  },
  mounted () {
    this.loadData()
  },
  methods: {
    loadData () {
      if(this.code !== null && this.code !== '') {
        HTTP.get(`/hkmainland/fetch_regular_reports?code=${this.code}`).then(dt => {
          this.reports = dt.data.sort((a, b) => moment(b.date) - moment(a.date))
        })
      } else {
        this.reports = []
      }
    }
  },
  watch : {
    code () {
      this.loadData()
    }
  }
}
</script>

<style lang='scss' scoped>
.regular_report {

}
.regular_report table td {
  padding: 5px 10px 5px 2px;
  font-weight: 400;
}
.regular_report table tr td:last-child {
  padding-left: 30px;
}
</style>

