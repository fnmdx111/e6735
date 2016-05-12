jQuery = require 'jquery'
$ = jQuery
React = require 'react'
ReactDOM = require 'react-dom'

Uploader = React.createFactory(require('./Uploader'))

AbstractView = require './AbstractView'
ResultGrid = require './ResultGrid'
ScoreVector = React.createFactory(require './ScoreVector')
E = require './Els'

query_view = React.createClass
  render: ->
    E.div {},
      E.div {className: 'page-header'},
        E.h2 {}, "What's on your mind?"
      E.div {},
        E.ul {className: "nav nav-tabs", role: "tablist", id: "tab-uls"},
          E.li {role: "presentation", className: "active"},
            E.a {href: "#", id: "ahtg"},
              "Heterogeneous search"
          E.li {role: "presentation", className: ""},
            E.a {href: "#", id: "ahmg"},
              "Homogeneous search"
          E.li {role: "presentation", className: ""},
            E.a {href: "#", id: "ascores"},
              "Search by scores"
        E.div {className: "tab-content", id: "my-tab-content"},
          E.div {className: "panel panel-body", id: "htg"},
            Uploader {
              url: @props.htg_url
              evt_hnds: @props.evt_hnds1
              ref: 'htguploader'
            }
          E.div {className: "panel panel-body", id: "hmg"},
            Uploader {
              url: @props.hmg_url
              evt_hnds: @props.evt_hnds2
              ref: 'hmguploader'
            }
          E.div {className: "panel panel-body", id: "scores"},
            ScoreVector {id: "sos", child_col: 3}
            E.btn {id: "scores-submit", className: "btn btn-primary"},
              "Submit"
      E.hr {className: 'query-result invisible'}
      E.div {id: 'result-row', className: 'query-result invisible'}

  componentDidMount: ->
    $$p = @props
    $$p.grid.refresh_refs()

    $('#hmg').hide()
    $('#scores').hide()
    for it in ['htg', 'hmg', 'scores']
      $("#a#{it}").on 'click', ->
        $("#tab-uls > li").each ->
          $(this).removeClass 'active'
        $(this).addClass 'active'

        $("#my-tab-content > div").each ->
          $(this).hide()
        tab_id = "##{$(this).attr('id').substring(1)}"
        $(tab_id).show()

    $("#scores-submit").on 'click', ->
      $('.waiting').removeClass 'invisible'

      dims = ($("#dims-sos-#{id}").val() / 100.0 for id in [1..8])
      data = new FormData()
      data.append 'dims', dims
      $.ajax {
        url: 'sos'
        data: data
        processData: false
        contentType: false
        type: "POST"
        success: (data) =>
          $('.waiting').addClass 'invisible'
          switch data.status
            when 'failed'
              alert "Search failed! Reason: #{data.reason}."
            when 'successful'
              @grid.render data.data, null
        error: =>
          @grid.hide()
          $('.waiting').addClass 'invisible'
      }


module.exports = class VQuery extends AbstractView
  constructor: (@url='/htg-query', anchor_id='query') ->
    super '#' + anchor_id, anchor_id
    @refresh_refs()

    @grid = new ResultGrid 'result-row'

    @evt_hnds = {
      sending: (file) =>
        $('.waiting').removeClass('invisible')
        @grid.hide() if @grid.shown

      complete: (file) =>
        $('.waiting').addClass('invisible')

      success: (file, response) =>
        @grid.render response, file

      canceled: ->
        $('.waiting').addClass('invisible')
    }

    @evts1 = $.extend(true, {}, @evt_hnds)
    @evts2 = $.extend(true, {}, @evt_hnds)

  render: ->
    super()

    ReactDOM.render React.createElement(query_view, {
      htg_url: 'htgq'
      hmg_url: 'hmgq'
      evt_hnds1: @evts1
      evt_hnds2: @evts2
      grid: @grid
      parent: this
    }), @anchor
