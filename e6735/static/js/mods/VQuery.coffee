$ = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'

Uploader = React.createFactory(require('./Uploader'))

AbstractView = require './AbstractView'
ResultGrid = require './ResultGrid'

[_label, _input, _span, _btn, _img, _h2, _hr, _div, _p, _video] =\
  (React.createFactory(name) for name in\
  ['label', 'input', 'span', 'button', 'img', 'h2', 'hr', 'div', 'p', 'video'])

query_view = React.createClass
  render: ->
    _div {},
      _div {className: 'page-header'},
        _h2 {}, "What's on your mind?"
#        _div {className: "btn-group", 'data-toggle': "buttons", id: "qtype"},
#        _label {className: "btn btn-default active"},
#          _input {
#            type: "radio"
#            name: "qtype"
#            checked: true
#            value: "htg"
#            onChange: @props.on_htg_change
#          }
#          "Search heterogeneously."
#        _label {className: "btn btn-default"},
#          _input {
#            type: "radio"
#            name: "qtype"
#            checked: true
#            value: "hmg"
#            onChange: @props.on_hmg_change
#          }
#          "Search homogeneously."
      Uploader {
        url: @props.url
        evt_hnds: @props.evt_hnds
        ref: 'uploader'
      }
      _hr {className: 'query-result invisible'}
      _div {id: 'result-row', className: 'query-result invisible'}

  componentDidMount: ->
    $$p = @props
    $$p.grid.refresh_refs()


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

  render: ->
    super()

    ReactDOM.render React.createElement(query_view, {
      url: @url
      evt_hnds: @evt_hnds
      grid: @grid
      parent: this
    }), @anchor
