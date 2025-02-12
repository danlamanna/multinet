<template>
  <v-list
    class="item-panel"
    subheader
  >
    <v-subheader class="px-0">
      <h2 class="black--text">{{title}}</h2>

      <v-spacer />

      <v-tooltip top>
        <template v-slot:activator="{ on }">
          <v-scroll-x-transition>
            <v-btn
              icon
              small
              text
              v-if="anySelected"
              v-on="on"
            >
              <v-icon color="red accent-2" size="22px">delete_sweep</v-icon>
            </v-btn>
          </v-scroll-x-transition>
        </template>
        <span>Delete selected</span>
      </v-tooltip>

      <table-dialog
        v-if="isTable"
        :workspace="workspace"
        @success="$emit('new-table')"
      />
      <graph-dialog
        v-else
        :node-tables="nodeTables"
        :edge-tables="edgeTables"
        :workspace="workspace"
        @success="$emit('new-graph')"
      />

    </v-subheader>

    <v-divider></v-divider>

    <template v-if="items.length > 0">
      <v-hover
        v-for="item in items"
        :key="item"
      >
        <v-list-item
          active-class="grey lighten-4"
          ripple
          slot-scope="{ hover }"
          :to="`/workspaces/${workspace}/${routeType}/${item}`"
        >
          <v-list-item-action @click.prevent>
            <v-fade-transition hide-on-leave>
              <v-icon
                color="blue lighten-1"
                v-if="!hover && !checkbox[item]"
              >{{icon}}</v-icon>

              <v-checkbox
                class="ws-detail-checkbox"
                v-else
                v-model="checkbox[item]"
              ></v-checkbox>
            </v-fade-transition>
          </v-list-item-action>

          <v-list-item-content>
            <v-list-item-title>{{item}}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-hover>
    </template>
    <div
      class="ws-detail-empty-list"
      v-else
    >
      <v-icon color="blue lighten-1">info</v-icon> There's nothing here yet...
    </div>
  </v-list>
</template>

<script lang="ts">
import Vue from 'vue';
import TableDialog from '@/components/TableDialog.vue';
import GraphDialog from '@/components/GraphDialog.vue';

export default Vue.extend({
  name: 'ItemPanel',
  components: {
    GraphDialog,
    TableDialog,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    items: {
      type: Array,
      required: true,
    },
    workspace: {
      type: String,
      required: true,
    },
    nodeTables: {
      type: Array,
      required: false,
    },
    edgeTables: {
      type: Array,
      required: false,
    },
    routeType: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      checkbox: {},
    };
  },
  computed: {
    isTable(): boolean {
      return this.title === 'Tables';
    },

    anySelected(): boolean {
      return Object.values(this.checkbox)
        .some((d) => !!d);
    },
  },
});
</script>

<style scoped>
.v-list.item-panel {
  background: none;
}

.ws-detail-empty-list {
  padding: 40px 40px 55px;
  text-align: center;
}
</style>
