$ = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'

dropzone = React.createFactory(require('react-dropzone-component'))

AbstractView = require './AbstractView'
ResultGrid = require './ResultGrid'

[_img, _h2, _hr, _div, _p, _video] = (React.createFactory(name) for name in\
  ['img', 'h2', 'hr', 'div', 'p', 'video'])


query_view = React.createClass
  render: ->
    _div {},
      _div {className: 'page-header'},
        _h2 {}, "What's on your mind?"
      dropzone {
        config: this.props.dz_cfg
        djsConfig: this.props.djs_cfg
        eventHandlers: this.props.evt_hnds
      }
      _hr {className: 'query-result'}
      _div {id: 'result-row', className: 'query-result invisible'}

  componentDidMount: ->
    this.props.grid.refresh_refs()


module.exports = class VQuery extends AbstractView
  constructor: (url='/query', anchor_id='query') ->
    super '#' + anchor_id, anchor_id
    @refresh_refs()

    @search_box_cfg =
      iconFiletypes: ['mp4', 'mp3', 'ogg']
      showFiletypeIcon: true
      postUrl: url

    @grid = new ResultGrid 'result-row'

    @evt_hnds = {
      init: (dz) =>
        dz.options.accept = (file, done) ->
          this.removeFile(this.files[0]) while this.files.length > 1
          done()
        dz.options.acceptedFiles = 'video/*,audio/*'

      sending: (file) =>
        $('.waiting').removeClass('invisible')
        @grid.hide() if @grid.shown

      complete: (file) =>
        $('.waiting').addClass('invisible')

      success: (file, response) =>
        @grid.render response, file

      canceled: ->
        $('.waiting').addClass('invisible')
        alert 'failed'
    }

  render: ->
    super()

    ReactDOM.render React.createElement(query_view, {
      dz_cfg: @search_box_cfg
      djs_cfg: {}
      evt_hnds: @evt_hnds
      grid: @grid
    }), @anchor
